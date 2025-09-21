"""
File optimization service for handling large files
"""

import os
import io
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import tempfile
import asyncio
import aiofiles

# Document processing libraries
import PyPDF2
from docx import Document as DocxDocument
from PIL import Image

logger = logging.getLogger(__name__)

class FileOptimizer:
    """Optimize large files for better processing"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "ai_analyst_temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def optimize_file(self, file_path: str, target_size_mb: int = 50) -> Tuple[str, Dict[str, Any]]:
        """
        Optimize a file to reduce its size while preserving content quality
        Returns: (optimized_file_path, optimization_info)
        """
        
        original_size = Path(file_path).stat().st_size
        target_size = target_size_mb * 1024 * 1024
        
        if original_size <= target_size:
            return file_path, {"optimization": "none_needed", "original_size_mb": original_size / 1024 / 1024}
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return await self._optimize_pdf(file_path, target_size)
        elif file_extension in ['.docx', '.doc']:
            return await self._optimize_docx(file_path, target_size)
        else:
            # For unsupported types, just return original
            return file_path, {"optimization": "unsupported_type", "original_size_mb": original_size / 1024 / 1024}
    
    async def _optimize_pdf(self, file_path: str, target_size: int) -> Tuple[str, Dict[str, Any]]:
        """Optimize PDF by removing images and compressing"""
        
        try:
            original_size = Path(file_path).stat().st_size
            
            async with aiofiles.open(file_path, 'rb') as file:
                content = await file.read()
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            pdf_writer = PyPDF2.PdfWriter()
            
            # Copy pages without images to reduce size
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    # Remove images from page
                    if '/XObject' in page['/Resources']:
                        xObject = page['/Resources']['/XObject'].get_object()
                        for obj in xObject:
                            if xObject[obj]['/Subtype'] == '/Image':
                                # Replace image with small placeholder
                                del xObject[obj]
                    
                    pdf_writer.add_page(page)
                except Exception as e:
                    logger.warning(f"Failed to optimize page {page_num}: {e}")
                    # Add page as-is if optimization fails
                    pdf_writer.add_page(page)
            
            # Save optimized PDF
            optimized_path = self.temp_dir / f"optimized_{Path(file_path).name}"
            
            async with aiofiles.open(optimized_path, 'wb') as output_file:
                output_buffer = io.BytesIO()
                pdf_writer.write(output_buffer)
                await output_file.write(output_buffer.getvalue())
            
            optimized_size = optimized_path.stat().st_size
            
            optimization_info = {
                "optimization": "pdf_compression",
                "original_size_mb": original_size / 1024 / 1024,
                "optimized_size_mb": optimized_size / 1024 / 1024,
                "size_reduction_percent": ((original_size - optimized_size) / original_size) * 100,
                "method": "removed_images_and_compressed"
            }
            
            # If still too large, try more aggressive optimization
            if optimized_size > target_size:
                return await self._aggressive_pdf_optimization(str(optimized_path), target_size, optimization_info)
            
            return str(optimized_path), optimization_info
            
        except Exception as e:
            logger.error(f"PDF optimization failed: {e}")
            return file_path, {"optimization": "failed", "error": str(e)}
    
    async def _aggressive_pdf_optimization(self, file_path: str, target_size: int, prev_info: Dict) -> Tuple[str, Dict[str, Any]]:
        """More aggressive PDF optimization - extract text only"""
        
        try:
            async with aiofiles.open(file_path, 'rb') as file:
                content = await file.read()
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            
            # Extract all text
            all_text = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        all_text.append(f"--- Page {page_num + 1} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num}: {e}")
            
            # Create a simple text-only PDF
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            text_only_path = self.temp_dir / f"text_only_{Path(file_path).name}"
            
            c = canvas.Canvas(str(text_only_path), pagesize=letter)
            width, height = letter
            
            y_position = height - 50
            line_height = 12
            
            for text_block in all_text:
                lines = text_block.split('\n')
                for line in lines:
                    if y_position < 50:  # Start new page
                        c.showPage()
                        y_position = height - 50
                    
                    # Wrap long lines
                    if len(line) > 80:
                        words = line.split()
                        current_line = ""
                        for word in words:
                            if len(current_line + word) > 80:
                                if current_line:
                                    c.drawString(50, y_position, current_line)
                                    y_position -= line_height
                                current_line = word + " "
                            else:
                                current_line += word + " "
                        if current_line:
                            c.drawString(50, y_position, current_line)
                            y_position -= line_height
                    else:
                        c.drawString(50, y_position, line)
                        y_position -= line_height
            
            c.save()
            
            optimized_size = text_only_path.stat().st_size
            original_size = prev_info["original_size_mb"] * 1024 * 1024
            
            optimization_info = {
                "optimization": "aggressive_text_only",
                "original_size_mb": prev_info["original_size_mb"],
                "optimized_size_mb": optimized_size / 1024 / 1024,
                "size_reduction_percent": ((original_size - optimized_size) / original_size) * 100,
                "method": "text_extraction_only",
                "warning": "Images and formatting removed to reduce size"
            }
            
            return str(text_only_path), optimization_info
            
        except Exception as e:
            logger.error(f"Aggressive PDF optimization failed: {e}")
            return file_path, {"optimization": "failed", "error": str(e)}
    
    async def _optimize_docx(self, file_path: str, target_size: int) -> Tuple[str, Dict[str, Any]]:
        """Optimize DOCX by removing images and reducing formatting"""
        
        try:
            original_size = Path(file_path).stat().st_size
            
            async with aiofiles.open(file_path, 'rb') as file:
                content = await file.read()
            
            doc = DocxDocument(io.BytesIO(content))
            
            # Remove images to reduce size
            for shape in doc.inline_shapes:
                try:
                    shape._element.getparent().remove(shape._element)
                except:
                    pass
            
            # Create optimized version
            optimized_path = self.temp_dir / f"optimized_{Path(file_path).name}"
            doc.save(str(optimized_path))
            
            optimized_size = optimized_path.stat().st_size
            
            optimization_info = {
                "optimization": "docx_compression",
                "original_size_mb": original_size / 1024 / 1024,
                "optimized_size_mb": optimized_size / 1024 / 1024,
                "size_reduction_percent": ((original_size - optimized_size) / original_size) * 100,
                "method": "removed_images"
            }
            
            return str(optimized_path), optimization_info
            
        except Exception as e:
            logger.error(f"DOCX optimization failed: {e}")
            return file_path, {"optimization": "failed", "error": str(e)}
    
    def cleanup_temp_files(self):
        """Clean up temporary optimization files"""
        try:
            for temp_file in self.temp_dir.glob("optimized_*"):
                temp_file.unlink()
            for temp_file in self.temp_dir.glob("text_only_*"):
                temp_file.unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")

# Global instance
file_optimizer = FileOptimizer()
