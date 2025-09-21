"""
Main FastAPI application for AI Startup Analyst Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import analysis, upload, benchmarks, dashboard, progress


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    setup_logging()
    logging.info("🚀 AI Startup Analyst Backend starting up...")
    
    yield
    
    # Shutdown
    logging.info("🛑 AI Startup Analyst Backend shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered startup analysis and benchmarking platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Startup Analyst Backend",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Startup Analyst Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Include API routes
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(benchmarks.router, prefix="/api", tags=["benchmarks"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(progress.router, prefix="/api", tags=["progress"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logging.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
