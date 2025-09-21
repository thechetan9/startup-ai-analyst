"""
Dashboard API routes for analytics and overview
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview():
    """Get dashboard overview with key metrics"""
    
    try:
        # Mock dashboard data
        overview = {
            "summary": {
                "total_startups_analyzed": 47,
                "analyses_this_month": 12,
                "average_score": 72.3,
                "high_potential_startups": 8
            },
            "recent_analyses": [
                {
                    "startup_id": "ed22e65e-759c-4ffa-aa68-67b7b248e617",
                    "company_name": "TechFlow AI",
                    "score": 85.2,
                    "recommendation": "INVEST",
                    "analyzed_at": (datetime.now() - timedelta(hours=2)).isoformat()
                },
                {
                    "startup_id": str(uuid.uuid4()),
                    "company_name": "HealthSync Pro",
                    "score": 78.9,
                    "recommendation": "MONITOR",
                    "analyzed_at": (datetime.now() - timedelta(hours=5)).isoformat()
                },
                {
                    "startup_id": str(uuid.uuid4()),
                    "company_name": "EduTech Solutions",
                    "score": 91.5,
                    "recommendation": "INVEST",
                    "analyzed_at": (datetime.now() - timedelta(days=1)).isoformat()
                }
            ],
            "sector_distribution": [
                {"sector": "fintech", "count": 12, "avg_score": 75.2},
                {"sector": "healthtech", "count": 8, "avg_score": 78.9},
                {"sector": "edtech", "count": 6, "avg_score": 82.1},
                {"sector": "saas", "count": 10, "avg_score": 71.8},
                {"sector": "e-commerce", "count": 7, "avg_score": 69.3},
                {"sector": "ai_ml", "count": 4, "avg_score": 88.7}
            ],
            "score_distribution": {
                "excellent": {"range": "90-100", "count": 5},
                "good": {"range": "80-89", "count": 12},
                "average": {"range": "70-79", "count": 18},
                "below_average": {"range": "60-69", "count": 8},
                "poor": {"range": "0-59", "count": 4}
            },
            "monthly_trends": [
                {"month": "2024-01", "analyses": 8, "avg_score": 71.2},
                {"month": "2024-02", "analyses": 12, "avg_score": 73.8},
                {"month": "2024-03", "analyses": 15, "avg_score": 72.9},
                {"month": "2024-04", "analyses": 12, "avg_score": 72.3}
            ]
        }
        
        return overview
        
    except Exception as e:
        logger.error(f"Dashboard overview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard overview failed: {str(e)}")


@router.get("/analytics")
async def get_analytics_data(
    time_period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    stage: Optional[str] = Query(None, description="Filter by funding stage")
):
    """Get detailed analytics data"""
    
    try:
        analytics = {
            "time_period": time_period,
            "filters": {"sector": sector, "stage": stage},
            "performance_metrics": {
                "total_analyses": 47,
                "avg_processing_time": 3.2,
                "accuracy_score": 0.89,
                "user_satisfaction": 4.6
            },
            "investment_recommendations": {
                "invest": {"count": 15, "percentage": 31.9},
                "monitor": {"count": 22, "percentage": 46.8},
                "pass": {"count": 10, "percentage": 21.3}
            },
            "risk_analysis": {
                "low_risk": {"count": 18, "percentage": 38.3},
                "medium_risk": {"count": 20, "percentage": 42.6},
                "high_risk": {"count": 7, "percentage": 14.9},
                "critical_risk": {"count": 2, "percentage": 4.3}
            },
            "top_performing_sectors": [
                {"sector": "ai_ml", "avg_score": 88.7, "count": 4},
                {"sector": "edtech", "avg_score": 82.1, "count": 6},
                {"sector": "healthtech", "avg_score": 78.9, "count": 8}
            ],
            "common_risk_flags": [
                {"risk_type": "Financial Risk", "frequency": 23, "avg_severity": "medium"},
                {"risk_type": "Market Risk", "frequency": 18, "avg_severity": "medium"},
                {"risk_type": "Team Risk", "frequency": 12, "avg_severity": "low"},
                {"risk_type": "Product Risk", "frequency": 15, "avg_severity": "medium"}
            ],
            "benchmark_performance": {
                "above_sector_median": 28,
                "top_quartile": 12,
                "top_decile": 5
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Analytics data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


@router.get("/portfolio")
async def get_portfolio_overview():
    """Get portfolio overview for tracked startups"""
    
    try:
        portfolio = {
            "total_startups": 47,
            "portfolio_value": 125000000,  # Total estimated value
            "top_performers": [
                {
                    "startup_id": "ed22e65e-759c-4ffa-aa68-67b7b248e617",
                    "company_name": "TechFlow AI",
                    "score": 85.2,
                    "valuation": 15000000,
                    "growth_rate": 0.45,
                    "last_updated": datetime.now().isoformat()
                },
                {
                    "startup_id": str(uuid.uuid4()),
                    "company_name": "EduTech Solutions",
                    "score": 91.5,
                    "valuation": 22000000,
                    "growth_rate": 0.62,
                    "last_updated": datetime.now().isoformat()
                }
            ],
            "watch_list": [
                {
                    "startup_id": str(uuid.uuid4()),
                    "company_name": "HealthSync Pro",
                    "score": 78.9,
                    "reason": "Strong team, needs market validation",
                    "next_review": (datetime.now() + timedelta(days=30)).isoformat()
                }
            ],
            "sector_allocation": [
                {"sector": "fintech", "count": 12, "percentage": 25.5},
                {"sector": "healthtech", "count": 8, "percentage": 17.0},
                {"sector": "edtech", "count": 6, "percentage": 12.8},
                {"sector": "saas", "count": 10, "percentage": 21.3},
                {"sector": "e-commerce", "count": 7, "percentage": 14.9},
                {"sector": "ai_ml", "count": 4, "percentage": 8.5}
            ],
            "stage_distribution": [
                {"stage": "seed", "count": 18, "percentage": 38.3},
                {"stage": "series_a", "count": 15, "percentage": 31.9},
                {"stage": "series_b", "count": 8, "percentage": 17.0},
                {"stage": "series_c", "count": 4, "percentage": 8.5},
                {"stage": "pre_seed", "count": 2, "percentage": 4.3}
            ]
        }
        
        return portfolio
        
    except Exception as e:
        logger.error(f"Portfolio overview failed: {e}")
        raise HTTPException(status_code=500, detail=f"Portfolio overview failed: {str(e)}")


@router.get("/alerts")
async def get_alerts_and_notifications():
    """Get alerts and notifications for important events"""
    
    try:
        alerts = {
            "critical_alerts": [
                {
                    "alert_id": str(uuid.uuid4()),
                    "type": "risk_flag",
                    "severity": "high",
                    "startup_id": str(uuid.uuid4()),
                    "company_name": "DataFlow Inc",
                    "message": "Significant drop in revenue growth detected",
                    "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                    "action_required": True
                }
            ],
            "notifications": [
                {
                    "notification_id": str(uuid.uuid4()),
                    "type": "analysis_complete",
                    "startup_id": "ed22e65e-759c-4ffa-aa68-67b7b248e617",
                    "company_name": "TechFlow AI",
                    "message": "Comprehensive analysis completed - Score: 85.2",
                    "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "read": False
                },
                {
                    "notification_id": str(uuid.uuid4()),
                    "type": "benchmark_update",
                    "message": "New benchmark data available for fintech sector",
                    "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
                    "read": False
                }
            ],
            "upcoming_reviews": [
                {
                    "startup_id": str(uuid.uuid4()),
                    "company_name": "HealthSync Pro",
                    "review_date": (datetime.now() + timedelta(days=7)).isoformat(),
                    "review_type": "quarterly_update"
                },
                {
                    "startup_id": str(uuid.uuid4()),
                    "company_name": "EduTech Solutions",
                    "review_date": (datetime.now() + timedelta(days=14)).isoformat(),
                    "review_type": "funding_round_analysis"
                }
            ]
        }
        
        return alerts
        
    except Exception as e:
        logger.error(f"Alerts retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Alerts failed: {str(e)}")


@router.get("/reports")
async def get_available_reports():
    """Get list of available reports"""
    
    try:
        reports = {
            "standard_reports": [
                {
                    "report_id": "sector_analysis",
                    "name": "Sector Analysis Report",
                    "description": "Comprehensive analysis of startup performance by sector",
                    "last_generated": (datetime.now() - timedelta(days=1)).isoformat()
                },
                {
                    "report_id": "monthly_summary",
                    "name": "Monthly Investment Summary",
                    "description": "Monthly summary of analyses and recommendations",
                    "last_generated": (datetime.now() - timedelta(days=3)).isoformat()
                },
                {
                    "report_id": "risk_assessment",
                    "name": "Portfolio Risk Assessment",
                    "description": "Risk analysis across all tracked startups",
                    "last_generated": (datetime.now() - timedelta(days=7)).isoformat()
                }
            ],
            "custom_reports": [
                {
                    "report_id": str(uuid.uuid4()),
                    "name": "AI/ML Startup Deep Dive",
                    "description": "Custom analysis of AI/ML sector startups",
                    "created_by": "analyst_user",
                    "created_at": (datetime.now() - timedelta(days=5)).isoformat()
                }
            ]
        }
        
        return reports
        
    except Exception as e:
        logger.error(f"Reports retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reports failed: {str(e)}")


@router.post("/reports/generate")
async def generate_custom_report(
    report_type: str,
    filters: Dict[str, Any],
    include_charts: bool = True,
    format: str = "pdf"
):
    """Generate a custom report"""
    
    try:
        report_id = str(uuid.uuid4())
        
        # Mock report generation
        report_info = {
            "report_id": report_id,
            "report_type": report_type,
            "filters": filters,
            "status": "generating",
            "estimated_completion": (datetime.now() + timedelta(minutes=5)).isoformat(),
            "format": format,
            "include_charts": include_charts,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "message": "Report generation initiated",
            "report_info": report_info
        }
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/export")
async def export_data(
    data_type: str = Query(..., description="Type of data to export: startups, analyses, benchmarks"),
    format: str = Query("csv", description="Export format: csv, json, xlsx"),
    filters: Optional[str] = Query(None, description="JSON string of filters")
):
    """Export data in various formats"""
    
    try:
        export_id = str(uuid.uuid4())
        
        export_info = {
            "export_id": export_id,
            "data_type": data_type,
            "format": format,
            "filters": filters,
            "status": "preparing",
            "estimated_size": "2.5 MB",
            "estimated_completion": (datetime.now() + timedelta(minutes=2)).isoformat(),
            "download_url": f"/api/v1/dashboard/download/{export_id}",
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        return {
            "message": "Data export initiated",
            "export_info": export_info
        }
        
    except Exception as e:
        logger.error(f"Data export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Data export failed: {str(e)}")
