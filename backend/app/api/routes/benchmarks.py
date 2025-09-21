"""
Benchmarking API routes for startup comparison
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.core.config import settings
from app.models.startup import BenchmarkData

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sectors")
async def get_available_sectors():
    """Get list of available sectors for benchmarking"""
    
    try:
        # In a real implementation, this would query BigQuery
        sectors = [
            "fintech", "healthtech", "edtech", "e-commerce", "saas",
            "marketplace", "ai_ml", "blockchain", "iot", "cybersecurity",
            "mobility", "real_estate", "food_tech", "gaming", "media"
        ]
        
        return {
            "sectors": sectors,
            "total_count": len(sectors),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Sectors retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sectors: {str(e)}")


@router.get("/stages")
async def get_funding_stages():
    """Get list of funding stages for benchmarking"""
    
    try:
        stages = [
            {"stage": "pre_seed", "description": "Pre-seed funding"},
            {"stage": "seed", "description": "Seed funding"},
            {"stage": "series_a", "description": "Series A funding"},
            {"stage": "series_b", "description": "Series B funding"},
            {"stage": "series_c", "description": "Series C funding"},
            {"stage": "series_d_plus", "description": "Series D+ funding"},
            {"stage": "ipo", "description": "IPO/Public"},
            {"stage": "acquired", "description": "Acquired"}
        ]
        
        return {
            "stages": stages,
            "total_count": len(stages)
        }
        
    except Exception as e:
        logger.error(f"Stages retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stages: {str(e)}")


@router.get("/metrics")
async def get_benchmark_metrics(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    stage: Optional[str] = Query(None, description="Filter by funding stage"),
    limit: int = Query(50, description="Limit number of results")
):
    """Get benchmark metrics for comparison"""
    
    try:
        # Mock benchmark data - in real implementation, query BigQuery
        benchmark_metrics = [
            {
                "metric_name": "Revenue Growth Rate (YoY)",
                "sector": sector or "fintech",
                "stage": stage or "series_a",
                "percentile_25": 0.15,
                "percentile_50": 0.30,
                "percentile_75": 0.50,
                "percentile_90": 0.75,
                "unit": "percentage",
                "sample_size": 150
            },
            {
                "metric_name": "Customer Acquisition Cost",
                "sector": sector or "fintech",
                "stage": stage or "series_a",
                "percentile_25": 50.0,
                "percentile_50": 120.0,
                "percentile_75": 200.0,
                "percentile_90": 350.0,
                "unit": "USD",
                "sample_size": 145
            },
            {
                "metric_name": "Monthly Recurring Revenue",
                "sector": sector or "fintech",
                "stage": stage or "series_a",
                "percentile_25": 50000.0,
                "percentile_50": 150000.0,
                "percentile_75": 400000.0,
                "percentile_90": 800000.0,
                "unit": "USD",
                "sample_size": 120
            },
            {
                "metric_name": "Gross Margin",
                "sector": sector or "fintech",
                "stage": stage or "series_a",
                "percentile_25": 0.45,
                "percentile_50": 0.65,
                "percentile_75": 0.80,
                "percentile_90": 0.90,
                "unit": "percentage",
                "sample_size": 180
            },
            {
                "metric_name": "Employee Count",
                "sector": sector or "fintech",
                "stage": stage or "series_a",
                "percentile_25": 8.0,
                "percentile_50": 15.0,
                "percentile_75": 25.0,
                "percentile_90": 45.0,
                "unit": "count",
                "sample_size": 200
            }
        ]
        
        return {
            "metrics": benchmark_metrics[:limit],
            "filters": {
                "sector": sector,
                "stage": stage,
                "limit": limit
            },
            "total_count": len(benchmark_metrics),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Benchmark metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")


@router.post("/compare")
async def compare_startup_to_benchmarks(
    startup_metrics: Dict[str, float],
    sector: str,
    stage: str
):
    """Compare startup metrics against sector benchmarks"""
    
    try:
        comparison_results = []
        
        # Get benchmark data for the sector/stage
        benchmark_response = await get_benchmark_metrics(sector=sector, stage=stage)
        benchmarks = benchmark_response["metrics"]
        
        for metric_name, startup_value in startup_metrics.items():
            # Find matching benchmark
            benchmark = next(
                (b for b in benchmarks if b["metric_name"].lower().replace(" ", "_") == metric_name.lower()),
                None
            )
            
            if benchmark:
                # Calculate percentile rank
                percentile_rank = calculate_percentile_rank(
                    startup_value,
                    benchmark["percentile_25"],
                    benchmark["percentile_50"],
                    benchmark["percentile_75"],
                    benchmark["percentile_90"]
                )
                
                # Determine performance rating
                performance_rating = get_performance_rating(percentile_rank)
                
                comparison_results.append({
                    "metric_name": benchmark["metric_name"],
                    "startup_value": startup_value,
                    "sector_median": benchmark["percentile_50"],
                    "sector_p75": benchmark["percentile_75"],
                    "sector_p90": benchmark["percentile_90"],
                    "percentile_rank": percentile_rank,
                    "performance_rating": performance_rating,
                    "unit": benchmark["unit"],
                    "sample_size": benchmark["sample_size"]
                })
        
        # Calculate overall benchmark score
        overall_score = sum(r["percentile_rank"] for r in comparison_results) / len(comparison_results) * 100
        
        return {
            "startup_id": "comparison_result",
            "sector": sector,
            "stage": stage,
            "overall_benchmark_score": round(overall_score, 1),
            "comparison_results": comparison_results,
            "summary": {
                "metrics_compared": len(comparison_results),
                "above_median": len([r for r in comparison_results if r["percentile_rank"] > 0.5]),
                "top_quartile": len([r for r in comparison_results if r["percentile_rank"] > 0.75]),
                "top_decile": len([r for r in comparison_results if r["percentile_rank"] > 0.9])
            },
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Benchmark comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/trends")
async def get_market_trends(
    sector: Optional[str] = Query(None),
    metric: Optional[str] = Query(None),
    time_period: str = Query("12m", description="Time period: 6m, 12m, 24m")
):
    """Get market trends and historical benchmark data"""
    
    try:
        # Mock trend data
        trend_data = {
            "sector": sector or "fintech",
            "metric": metric or "revenue_growth_rate",
            "time_period": time_period,
            "trend_direction": "increasing",
            "trend_strength": 0.75,
            "data_points": [
                {"period": "2024-Q1", "median": 0.25, "p75": 0.40, "p90": 0.60},
                {"period": "2024-Q2", "median": 0.28, "p75": 0.43, "p90": 0.65},
                {"period": "2024-Q3", "median": 0.30, "p75": 0.45, "p90": 0.68},
                {"period": "2024-Q4", "median": 0.32, "p75": 0.48, "p90": 0.70}
            ],
            "insights": [
                "Revenue growth rates have increased 28% over the past year",
                "Top performers are pulling ahead of the median",
                "Market conditions favor growth-focused startups"
            ]
        }
        
        return trend_data
        
    except Exception as e:
        logger.error(f"Trends retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trends: {str(e)}")


@router.get("/peer-analysis")
async def get_peer_analysis(
    startup_id: str,
    sector: str,
    stage: str,
    include_anonymous: bool = Query(True, description="Include anonymous peer data")
):
    """Get peer analysis for a specific startup"""
    
    try:
        # Mock peer analysis data
        peer_analysis = {
            "startup_id": startup_id,
            "sector": sector,
            "stage": stage,
            "peer_count": 25,
            "ranking": {
                "overall_rank": 8,
                "percentile": 68,
                "rank_change": "+3"
            },
            "metric_rankings": [
                {"metric": "Revenue Growth", "rank": 5, "percentile": 80},
                {"metric": "Customer Acquisition", "rank": 12, "percentile": 52},
                {"metric": "Team Size", "rank": 15, "percentile": 40},
                {"metric": "Funding Efficiency", "rank": 7, "percentile": 72}
            ],
            "similar_companies": [
                {"name": "Anonymous Peer A", "similarity_score": 0.85, "stage": stage},
                {"name": "Anonymous Peer B", "similarity_score": 0.78, "stage": stage},
                {"name": "Anonymous Peer C", "similarity_score": 0.72, "stage": stage}
            ],
            "competitive_advantages": [
                "Above-average revenue growth",
                "Strong technical team",
                "Efficient capital utilization"
            ],
            "areas_for_improvement": [
                "Customer acquisition efficiency",
                "Market expansion strategy",
                "Operational scaling"
            ]
        }
        
        return peer_analysis
        
    except Exception as e:
        logger.error(f"Peer analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Peer analysis failed: {str(e)}")


def calculate_percentile_rank(value: float, p25: float, p50: float, p75: float, p90: float) -> float:
    """Calculate percentile rank for a value given benchmark percentiles"""
    
    if value <= p25:
        return 0.25 * (value / p25) if p25 > 0 else 0.0
    elif value <= p50:
        return 0.25 + 0.25 * ((value - p25) / (p50 - p25))
    elif value <= p75:
        return 0.50 + 0.25 * ((value - p50) / (p75 - p50))
    elif value <= p90:
        return 0.75 + 0.15 * ((value - p75) / (p90 - p75))
    else:
        return 0.90 + 0.10 * min(1.0, (value - p90) / p90)


def get_performance_rating(percentile_rank: float) -> str:
    """Get performance rating from percentile rank"""
    
    if percentile_rank >= 0.9:
        return "Excellent"
    elif percentile_rank >= 0.75:
        return "Above Average"
    elif percentile_rank >= 0.5:
        return "Average"
    elif percentile_rank >= 0.25:
        return "Below Average"
    else:
        return "Poor"
