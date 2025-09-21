"""
Progress tracking API routes
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Optional
import logging

from app.services.progress_tracker import progress_tracker

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/progress/{document_id}")
async def get_document_progress(document_id: str):
    """Get progress for a specific document"""
    
    try:
        progress_data = progress_tracker.get_progress(document_id)
        
        if not progress_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No progress data found for document {document_id}"
            )
        
        return {
            "success": True,
            "document_id": document_id,
            "progress": progress_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get progress for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@router.get("/progress")
async def get_all_progress():
    """Get progress for all documents"""
    
    try:
        all_progress = progress_tracker.get_all_progress()
        
        return {
            "success": True,
            "total_documents": len(all_progress),
            "progress_data": all_progress
        }
        
    except Exception as e:
        logger.error(f"Failed to get all progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@router.delete("/progress/{document_id}")
async def clear_document_progress(document_id: str):
    """Clear progress data for a specific document"""
    
    try:
        progress_data = progress_tracker.get_progress(document_id)
        
        if not progress_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No progress data found for document {document_id}"
            )
        
        # Remove from tracker
        if document_id in progress_tracker._progress_data:
            del progress_tracker._progress_data[document_id]
        
        if document_id in progress_tracker._callbacks:
            del progress_tracker._callbacks[document_id]
        
        return {
            "success": True,
            "message": f"Progress data cleared for document {document_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clear progress for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear progress: {str(e)}")


@router.post("/progress/cleanup")
async def cleanup_old_progress(max_age_hours: int = 24):
    """Clean up old progress data"""
    
    try:
        initial_count = len(progress_tracker._progress_data)
        progress_tracker.cleanup_old_progress(max_age_hours)
        final_count = len(progress_tracker._progress_data)
        
        cleaned_count = initial_count - final_count
        
        return {
            "success": True,
            "message": f"Cleaned up {cleaned_count} old progress entries",
            "initial_count": initial_count,
            "final_count": final_count,
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup progress data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup: {str(e)}")


@router.get("/health")
async def progress_health_check():
    """Health check for progress tracking service"""
    
    try:
        total_documents = len(progress_tracker._progress_data)
        active_documents = len([
            doc for doc in progress_tracker._progress_data.values() 
            if not doc.get("completed", False)
        ])
        
        return {
            "success": True,
            "service": "progress_tracker",
            "status": "healthy",
            "total_documents": total_documents,
            "active_documents": active_documents,
            "completed_documents": total_documents - active_documents
        }
        
    except Exception as e:
        logger.error(f"Progress health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
