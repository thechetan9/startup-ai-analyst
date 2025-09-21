"""
Main FastAPI application for AI Startup Analyst Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import time
from google.cloud import bigquery
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize BigQuery client
def get_bigquery_client():
    """Initialize BigQuery client with default credentials (Cloud Run service account)"""
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", "my-project-genai-464305")
        logger.info(f"🔧 Attempting to initialize BigQuery client for project: {project_id}")

        # Use default credentials (works with Cloud Run service account)
        client = bigquery.Client(project=project_id)

        # Test the connection
        logger.info(f"🧪 Testing BigQuery connection...")
        query = f"SELECT 1 as test"
        query_job = client.query(query)
        results = query_job.result()
        logger.info(f"✅ BigQuery client initialized and tested successfully for project: {project_id}")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize BigQuery client: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return None

# Global BigQuery client
bq_client = get_bigquery_client()

# Create FastAPI application
app = FastAPI(
    title="AI Startup Analyst",
    description="AI-powered startup analysis and benchmarking platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
        "version": "1.0.0",
        "environment": os.environ.get("GOOGLE_CLOUD_PROJECT_ID", "unknown")
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Startup Analyst Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }

# Test endpoint
@app.get("/api/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "Backend is working!",
        "timestamp": "2025-09-21",
        "status": "success"
    }

# Analyses endpoints
@app.get("/analyses")
async def get_analyses():
    """Get all analyses from BigQuery"""
    try:
        if not bq_client:
            logger.warning("BigQuery client not available")
            return {
                "analyses": [],
                "total": 0,
                "message": "BigQuery not available"
            }

        # Query BigQuery for analyses
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", "my-project-genai-464305")
        dataset_id = os.environ.get("BIGQUERY_DATASET_ID", "startup_analytics")

        query = f"""
        SELECT
            analysis_id,
            company_name,
            sector,
            score,
            recommendation,
            revenue,
            growth_rate,
            funding,
            analysis_timestamp,
            market_opportunity_score,
            team_quality_score,
            product_innovation_score,
            financial_potential_score,
            execution_capability_score
        FROM `{project_id}.{dataset_id}.analysis_results`
        ORDER BY analysis_timestamp DESC
        LIMIT 50
        """

        logger.info(f"Querying BigQuery: {query}")
        query_job = bq_client.query(query)
        results = query_job.result()

        analyses = []
        for row in results:
            analysis = {
                "id": row.analysis_id,
                "companyName": row.company_name,
                "sector": row.sector,
                "score": row.score,
                "recommendation": row.recommendation,
                "revenue": row.revenue,
                "growthRate": row.growth_rate,
                "funding": row.funding,
                "createdAt": row.analysis_timestamp.isoformat() if row.analysis_timestamp else None,
                "scoringBreakdown": {
                    "market_opportunity": row.market_opportunity_score,
                    "team_quality": row.team_quality_score,
                    "product_innovation": row.product_innovation_score,
                    "financial_potential": row.financial_potential_score,
                    "execution_capability": row.execution_capability_score
                }
            }
            analyses.append(analysis)

        logger.info(f"✅ Retrieved {len(analyses)} analyses from BigQuery")
        return {
            "analyses": analyses,
            "total": len(analyses),
            "message": f"Found {len(analyses)} analyses"
        }

    except Exception as e:
        logger.error(f"❌ Error retrieving analyses: {e}")
        return {
            "analyses": [],
            "total": 0,
            "message": f"Error retrieving analyses: {str(e)}"
        }

@app.post("/api/analyses")
async def save_analysis(analysis_data: dict):
    """Save analysis to BigQuery (placeholder)"""
    return {
        "success": True,
        "message": "Analysis saved successfully",
        "analysis_id": f"analysis-{analysis_data.get('company_name', 'unknown')}-{int(time.time())}"
    }

@app.post("/analyze")
async def analyze_files():
    """Analyze uploaded files (placeholder)"""
    return {
        "success": True,
        "message": "File analysis not implemented yet",
        "document_id": f"doc-{int(time.time())}"
    }

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
