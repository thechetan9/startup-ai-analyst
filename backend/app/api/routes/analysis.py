"""
Startup analysis API routes
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime

from app.models.startup import StartupAnalysis, StartupCreate, Startup
from app.models.documents import DocumentAnalysisRequest, DocumentAnalysisResult
from app.services.ai_analyzer import ai_analyzer
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/startup", response_model=dict)
async def analyze_startup(
    background_tasks: BackgroundTasks,
    startup_id: str,
    analysis_type: str = "comprehensive",
    include_benchmarking: bool = True,
    include_risk_assessment: bool = True,
    custom_weightings: Optional[Dict[str, float]] = None
):
    """Analyze a startup based on uploaded documents and data"""
    
    try:
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        logger.info(f"Starting startup analysis {analysis_id} for startup {startup_id}")
        
        # Add background task for analysis
        background_tasks.add_task(
            analyze_startup_background,
            analysis_id,
            startup_id,
            analysis_type,
            include_benchmarking,
            include_risk_assessment,
            custom_weightings or {}
        )
        
        return {
            "message": "Startup analysis initiated",
            "analysis_id": analysis_id,
            "startup_id": startup_id,
            "analysis_type": analysis_type,
            "status": "processing",
            "estimated_completion": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Analysis initiation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/startup/{startup_id}/results")
async def get_startup_analysis_results(startup_id: str):
    """Get analysis results for a startup"""
    
    try:
        # In a real implementation, this would query the database
        # For now, we'll return a mock comprehensive analysis
        
        mock_analysis = {
            "analysis_id": str(uuid.uuid4()),
            "startup_id": startup_id,
            "analysis_type": "comprehensive",
            "overall_score": 78.5,
            "financial_metrics": {
                "revenue": 2500000,
                "revenue_growth_rate": 0.45,
                "gross_margin": 0.72,
                "burn_rate": 180000,
                "runway_months": 18,
                "ltv_cac_ratio": 3.2
            },
            "traction_metrics": {
                "user_count": 15000,
                "user_growth_rate": 0.25,
                "customer_count": 450,
                "customer_growth_rate": 0.30
            },
            "team_metrics": {
                "employee_count": 25,
                "employee_growth_rate": 0.40,
                "engineering_ratio": 0.48,
                "founder_experience": "Strong technical background, previous exit"
            },
            "insights": [
                {
                    "category": "Growth",
                    "title": "Strong Revenue Growth",
                    "description": "45% YoY revenue growth indicates strong market traction",
                    "impact": "Positive indicator for scalability",
                    "confidence": 0.9
                },
                {
                    "category": "Financial",
                    "title": "Healthy Unit Economics",
                    "description": "LTV/CAC ratio of 3.2 shows sustainable customer acquisition",
                    "impact": "Strong foundation for profitability",
                    "confidence": 0.85
                }
            ],
            "risk_flags": [
                {
                    "flag_type": "Financial Risk",
                    "severity": "medium",
                    "description": "18-month runway requires funding within 12 months",
                    "confidence": 0.8
                }
            ],
            "benchmarks": [
                {
                    "metric_name": "Revenue Growth Rate",
                    "startup_value": 0.45,
                    "sector_median": 0.25,
                    "sector_p75": 0.40,
                    "percentile_rank": 0.78,
                    "performance_rating": "Above Average"
                }
            ],
            "investment_recommendation": "INVEST - Strong fundamentals with manageable risks",
            "key_strengths": [
                "Experienced founding team",
                "Strong revenue growth",
                "Healthy unit economics",
                "Clear market opportunity"
            ],
            "key_concerns": [
                "Limited runway requiring near-term funding",
                "Competitive market landscape",
                "Customer concentration risk"
            ],
            "next_steps": [
                "Conduct detailed due diligence on financials",
                "Interview key customers for validation",
                "Assess competitive positioning",
                "Review funding timeline and requirements"
            ],
            "created_at": datetime.now().isoformat()
        }
        
        return mock_analysis
        
    except Exception as e:
        logger.error(f"Results retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Results retrieval failed: {str(e)}")


@router.post("/documents", response_model=dict)
async def analyze_documents(
    background_tasks: BackgroundTasks,
    request: DocumentAnalysisRequest
):
    """Analyze specific documents for insights"""
    
    try:
        analysis_id = str(uuid.uuid4())
        
        logger.info(f"Starting document analysis {analysis_id} for documents: {request.document_ids}")
        
        # Add background task for document analysis
        background_tasks.add_task(
            analyze_documents_background,
            analysis_id,
            request.document_ids,
            request.analysis_type,
            request.custom_prompts or [],
            request.include_benchmarking,
            request.include_risk_assessment
        )
        
        return {
            "message": "Document analysis initiated",
            "analysis_id": analysis_id,
            "document_ids": request.document_ids,
            "analysis_type": request.analysis_type,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Document analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")


@router.get("/compare")
async def compare_startups(
    startup_ids: List[str],
    comparison_metrics: Optional[List[str]] = None
):
    """Compare multiple startups across key metrics"""
    
    try:
        if len(startup_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 startups required for comparison")
        
        # Mock comparison data
        comparison_result = {
            "comparison_id": str(uuid.uuid4()),
            "startup_ids": startup_ids,
            "metrics_compared": comparison_metrics or [
                "overall_score", "revenue_growth", "market_size", "team_strength"
            ],
            "comparison_data": {
                startup_id: {
                    "overall_score": 75 + (hash(startup_id) % 25),
                    "revenue_growth": 0.2 + (hash(startup_id) % 50) / 100,
                    "market_size": 1000000000 + (hash(startup_id) % 5000000000),
                    "team_strength": 7 + (hash(startup_id) % 3)
                } for startup_id in startup_ids
            },
            "winner_by_metric": {
                "overall_score": startup_ids[0],
                "revenue_growth": startup_ids[1] if len(startup_ids) > 1 else startup_ids[0],
                "market_size": startup_ids[0],
                "team_strength": startup_ids[-1]
            },
            "summary": f"Comparison of {len(startup_ids)} startups across key investment metrics",
            "created_at": datetime.now().isoformat()
        }
        
        return comparison_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Startup comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get status of an ongoing analysis"""
    
    try:
        # Mock status response
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "progress": 100,
            "estimated_completion": "Analysis complete",
            "current_step": "Generating final report",
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


async def analyze_startup_background(
    analysis_id: str,
    startup_id: str,
    analysis_type: str,
    include_benchmarking: bool,
    include_risk_assessment: bool,
    custom_weightings: Dict[str, float]
):
    """Background task for comprehensive startup analysis"""
    
    try:
        logger.info(f"Processing startup analysis {analysis_id}")
        
        # This would integrate with the AI analyzer service
        # For now, we'll simulate the analysis process
        
        # In a real implementation:
        # 1. Gather all documents for the startup
        # 2. Extract and structure data
        # 3. Run AI analysis with Gemini
        # 4. Generate benchmarks from BigQuery
        # 5. Assess risks and opportunities
        # 6. Create investment recommendation
        
        logger.info(f"Startup analysis {analysis_id} completed")
        
    except Exception as e:
        logger.error(f"Background startup analysis failed: {e}")


async def analyze_documents_background(
    analysis_id: str,
    document_ids: List[str],
    analysis_type: str,
    custom_prompts: List[str],
    include_benchmarking: bool,
    include_risk_assessment: bool
):
    """Background task for document analysis"""
    
    try:
        logger.info(f"Processing document analysis {analysis_id}")
        
        # This would process the specific documents
        # and extract insights using AI
        
        logger.info(f"Document analysis {analysis_id} completed")
        
    except Exception as e:
        logger.error(f"Background document analysis failed: {e}")


@router.post("/batch-analyze")
async def batch_analyze_startups(
    background_tasks: BackgroundTasks,
    startup_ids: List[str],
    analysis_type: str = "comprehensive"
):
    """Analyze multiple startups in batch (useful for your 14 companies)"""
    
    try:
        batch_id = str(uuid.uuid4())
        
        logger.info(f"Starting batch analysis {batch_id} for {len(startup_ids)} startups")
        
        # Add background task for batch analysis
        background_tasks.add_task(
            batch_analyze_background,
            batch_id,
            startup_ids,
            analysis_type
        )
        
        return {
            "message": f"Batch analysis initiated for {len(startup_ids)} startups",
            "batch_id": batch_id,
            "startup_ids": startup_ids,
            "analysis_type": analysis_type,
            "status": "processing",
            "estimated_completion": f"{len(startup_ids) * 2}-{len(startup_ids) * 5} minutes"
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


async def batch_analyze_background(
    batch_id: str,
    startup_ids: List[str],
    analysis_type: str
):
    """Background task for batch startup analysis"""
    
    try:
        logger.info(f"Processing batch analysis {batch_id}")
        
        for startup_id in startup_ids:
            # Process each startup
            analysis_id = str(uuid.uuid4())
            await analyze_startup_background(
                analysis_id, startup_id, analysis_type, True, True, {}
            )
        
        logger.info(f"Batch analysis {batch_id} completed")
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
