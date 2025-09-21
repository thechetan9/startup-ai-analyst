"""
Document upload and processing API routes
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import uuid
import aiofiles
from pathlib import Path
import logging

from app.models.documents import DocumentType, DocumentUpload, Document, ProcessingResult
from app.services.document_processor import document_processor
from app.services.progress_tracker import progress_tracker, create_progress_callback
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/single", response_model=dict)
async def upload_single_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    startup_id: str = Form(...),
    document_type: DocumentType = Form(...),
    description: Optional[str] = Form(None)
):
    """Upload a single document for processing"""
    
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.pdf', '.docx', '.doc']:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported: PDF, DOCX, DOC"
            )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Create safe filename
        safe_filename = f"{document_id}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"File uploaded: {safe_filename} for startup {startup_id}")
        
        # Add background task for processing
        background_tasks.add_task(
            process_document_background,
            str(file_path),
            document_type,
            startup_id,
            document_id
        )
        
        return {
            "message": "Document uploaded successfully",
            "document_id": document_id,
            "filename": file.filename,
            "startup_id": startup_id,
            "document_type": document_type.value,
            "status": "uploaded",
            "processing": "started"
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/batch", response_model=dict)
async def upload_multiple_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    startup_id: str = Form(...),
    document_types: List[DocumentType] = Form(...),
    descriptions: Optional[List[str]] = Form(None)
):
    """Upload multiple documents for batch processing"""
    
    try:
        if len(files) != len(document_types):
            raise HTTPException(
                status_code=400, 
                detail="Number of files must match number of document types"
            )
        
        uploaded_documents = []
        
        for i, (file, doc_type) in enumerate(zip(files, document_types)):
            if not file.filename:
                continue
            
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in ['.pdf', '.docx', '.doc']:
                logger.warning(f"Skipping unsupported file: {file.filename}")
                continue
            
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Create safe filename
            safe_filename = f"{document_id}_{file.filename}"
            file_path = UPLOAD_DIR / safe_filename
            
            # Save uploaded file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Add to processing queue
            background_tasks.add_task(
                process_document_background,
                str(file_path),
                doc_type,
                startup_id,
                document_id
            )
            
            uploaded_documents.append({
                "document_id": document_id,
                "filename": file.filename,
                "document_type": doc_type.value,
                "status": "uploaded"
            })
        
        logger.info(f"Batch upload completed: {len(uploaded_documents)} files for startup {startup_id}")
        
        return {
            "message": f"Successfully uploaded {len(uploaded_documents)} documents",
            "startup_id": startup_id,
            "documents": uploaded_documents,
            "processing": "started"
        }
        
    except Exception as e:
        logger.error(f"Batch upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")


@router.get("/status/{document_id}")
async def get_processing_status(document_id: str):
    """Get processing status of a document"""
    
    try:
        # In a real implementation, you'd check the database
        # For now, we'll return a mock status
        
        # Check if processed file exists
        processed_files = list(UPLOAD_DIR.glob(f"{document_id}_*"))
        
        if not processed_files:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": document_id,
            "status": "completed",  # This would come from database in real implementation
            "message": "Document processed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/process-existing")
async def process_existing_documents(
    background_tasks: BackgroundTasks,
    startup_id: str,
    document_folder: str = "company_documents"
):
    """Process existing documents from a folder (useful for your 14 company datasets)"""
    
    try:
        folder_path = Path(document_folder)
        if not folder_path.exists():
            raise HTTPException(status_code=404, detail=f"Folder not found: {document_folder}")
        
        processed_documents = []
        
        # Find all PDF and DOCX files in the folder
        supported_extensions = ['.pdf', '.docx', '.doc']
        document_files = []
        
        for ext in supported_extensions:
            document_files.extend(folder_path.glob(f"*{ext}"))
        
        if not document_files:
            raise HTTPException(
                status_code=404, 
                detail="No supported documents found in folder"
            )
        
        for file_path in document_files:
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Determine document type based on filename patterns
            doc_type = _determine_document_type(file_path.name)
            
            # Add to processing queue
            background_tasks.add_task(
                process_document_background,
                str(file_path),
                doc_type,
                startup_id,
                document_id
            )
            
            processed_documents.append({
                "document_id": document_id,
                "filename": file_path.name,
                "document_type": doc_type.value,
                "status": "queued_for_processing"
            })
        
        logger.info(f"Queued {len(processed_documents)} existing documents for processing")
        
        return {
            "message": f"Successfully queued {len(processed_documents)} documents for processing",
            "startup_id": startup_id,
            "documents": processed_documents,
            "folder_path": str(folder_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Existing document processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


async def process_document_background(
    file_path: str,
    document_type: DocumentType,
    startup_id: str,
    document_id: str
):
    """Background task for document processing with progress tracking"""

    try:
        logger.info(f"Starting background processing for document {document_id}")

        # Start progress tracking
        progress_tracker.start_tracking(document_id)
        progress_callback = create_progress_callback(document_id)

        # Process the document with progress tracking
        result = await document_processor.process_document(
            file_path=file_path,
            document_type=document_type,
            startup_id=startup_id,
            progress_callback=progress_callback
        )

        # Mark as completed
        progress_tracker.complete_tracking(document_id, success=True, message="Processing completed successfully")

        logger.info(f"Document {document_id} processed successfully")

        # Save processing result to a JSON file for now
        import json
        result_path = UPLOAD_DIR / f"{document_id}_result.json"
        async with aiofiles.open(result_path, 'w') as f:
            await f.write(json.dumps(result.dict(), indent=2, default=str))
        
    except Exception as e:
        logger.error(f"Background processing failed for document {document_id}: {e}")


def _determine_document_type(filename: str) -> DocumentType:
    """Determine document type based on filename patterns"""
    
    filename_lower = filename.lower()
    
    if any(keyword in filename_lower for keyword in ['pitch', 'deck', 'presentation']):
        return DocumentType.PITCH_DECK
    elif any(keyword in filename_lower for keyword in ['financial', 'finance', 'statement', 'p&l', 'income']):
        return DocumentType.FINANCIAL_STATEMENT
    elif any(keyword in filename_lower for keyword in ['business', 'plan', 'strategy']):
        return DocumentType.BUSINESS_PLAN
    elif any(keyword in filename_lower for keyword in ['transcript', 'call', 'meeting']):
        return DocumentType.CALL_TRANSCRIPT
    elif any(keyword in filename_lower for keyword in ['email', 'correspondence']):
        return DocumentType.EMAIL
    elif any(keyword in filename_lower for keyword in ['update', 'report', 'progress']):
        return DocumentType.FOUNDER_UPDATE
    else:
        return DocumentType.OTHER


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its processing results"""
    
    try:
        # Find and delete document files
        deleted_files = []
        
        for file_path in UPLOAD_DIR.glob(f"{document_id}_*"):
            file_path.unlink()
            deleted_files.append(str(file_path))
        
        if not deleted_files:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "message": "Document deleted successfully",
            "document_id": document_id,
            "deleted_files": deleted_files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
