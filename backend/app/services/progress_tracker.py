"""
Progress tracking service for document processing
"""

import asyncio
import json
from typing import Dict, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Track processing progress for documents"""
    
    def __init__(self):
        self._progress_data: Dict[str, dict] = {}
        self._callbacks: Dict[str, list] = {}
    
    def start_tracking(self, document_id: str, total_steps: int = 100):
        """Start tracking progress for a document"""
        self._progress_data[document_id] = {
            "document_id": document_id,
            "progress": 0,
            "status": "starting",
            "message": "Initializing...",
            "total_steps": total_steps,
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "error": None,
            "completed": False
        }
        logger.info(f"Started tracking progress for document {document_id}")
    
    async def update_progress(
        self, 
        document_id: str, 
        progress: int, 
        message: str = "",
        status: str = "processing"
    ):
        """Update progress for a document"""
        if document_id not in self._progress_data:
            self.start_tracking(document_id)
        
        # Ensure progress is between 0 and 100
        progress = max(0, min(100, progress))
        
        self._progress_data[document_id].update({
            "progress": progress,
            "message": message,
            "status": status,
            "updated_at": datetime.now().isoformat(),
            "completed": progress >= 100
        })
        
        # Handle error status
        if progress < 0:
            self._progress_data[document_id].update({
                "status": "error",
                "error": message,
                "completed": True
            })
        
        logger.info(f"Progress update for {document_id}: {progress}% - {message}")
        
        # Notify callbacks
        await self._notify_callbacks(document_id)
    
    def get_progress(self, document_id: str) -> Optional[dict]:
        """Get current progress for a document"""
        return self._progress_data.get(document_id)
    
    def get_all_progress(self) -> Dict[str, dict]:
        """Get progress for all documents"""
        return self._progress_data.copy()
    
    def complete_tracking(self, document_id: str, success: bool = True, message: str = ""):
        """Mark tracking as complete"""
        if document_id in self._progress_data:
            self._progress_data[document_id].update({
                "progress": 100 if success else -1,
                "status": "completed" if success else "error",
                "message": message or ("Processing completed successfully" if success else "Processing failed"),
                "completed": True,
                "updated_at": datetime.now().isoformat()
            })
            
            if not success:
                self._progress_data[document_id]["error"] = message
    
    def cleanup_old_progress(self, max_age_hours: int = 24):
        """Clean up old progress data"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for doc_id, data in self._progress_data.items():
            try:
                updated_time = datetime.fromisoformat(data["updated_at"]).timestamp()
                if updated_time < cutoff_time:
                    to_remove.append(doc_id)
            except (ValueError, KeyError):
                to_remove.append(doc_id)  # Remove invalid entries
        
        for doc_id in to_remove:
            del self._progress_data[doc_id]
            if doc_id in self._callbacks:
                del self._callbacks[doc_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old progress entries")
    
    def add_callback(self, document_id: str, callback: Callable):
        """Add a callback for progress updates"""
        if document_id not in self._callbacks:
            self._callbacks[document_id] = []
        self._callbacks[document_id].append(callback)
    
    async def _notify_callbacks(self, document_id: str):
        """Notify all callbacks for a document"""
        if document_id in self._callbacks:
            progress_data = self._progress_data[document_id]
            for callback in self._callbacks[document_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(progress_data)
                    else:
                        callback(progress_data)
                except Exception as e:
                    logger.error(f"Callback error for {document_id}: {e}")

# Global progress tracker instance
progress_tracker = ProgressTracker()


class ProgressCallback:
    """Helper class to create progress callbacks"""
    
    def __init__(self, document_id: str, tracker: ProgressTracker = None):
        self.document_id = document_id
        self.tracker = tracker or progress_tracker
    
    async def __call__(self, message: str, progress: int, status: str = "processing"):
        """Update progress"""
        await self.tracker.update_progress(
            self.document_id, 
            progress, 
            message, 
            status
        )


def create_progress_callback(document_id: str) -> ProgressCallback:
    """Create a progress callback for a document"""
    return ProgressCallback(document_id)
