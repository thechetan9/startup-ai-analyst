"""
Comprehensive benchmarking service for startup comparison
Uses BigQuery for sector analysis and statistical benchmarking
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

from app.core.config import settings
from app.models.startup import BenchmarkData, StartupStage
from app.core.database import get_bigquery_client

logger = logging.getLogger(__name__)


class BenchmarkingService:
    """Advanced benchmarking service for startup evaluation"""
    
    def __init__(self):
        self.bigquery_client = get_bigquery_client()
        self.dataset_id = f"{settings.google_cloud_project_id}.{settings.bigquery_dataset_id}"
        
        # Initialize benchmark data if not exists
        asyncio.create_task(self._initialize_benchmark_data())
    
    async def _initialize_benchmark_data(self):
        """Initialize benchmark data in BigQuery"""
        try:
            await self._create_sample_benchmark_data()
            logger.info("Benchmark data initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize benchmark data: {e}")
    
    async def _create_sample_benchmark_data(self):
        """Create sample benchmark data for different sectors and stages"""
        
        # Sample benchmark data for different sectors and stages
        benchmark_data = [
            # FinTech benchmarks
            {"sector": "fintech", "stage": "seed", "metric_name": "revenue_growth_rate", "p25": 0.15, "p50": 0.30, "p75": 0.50, "p90": 0.75, "sample_size": 150},
            {"sector": "fintech", "stage": "seed", "metric_name": "customer_acquisition_cost", "p25": 50.0, "p50": 120.0, "p75": 200.0, "p90": 350.0, "sample_size": 145},
            {"sector": "fintech", "stage": "seed", "metric_name": "monthly_recurring_revenue", "p25": 25000.0, "p50": 75000.0, "p75": 150000.0, "p90": 300000.0, "sample_size": 120},
            {"sector": "fintech", "stage": "seed", "metric_name": "gross_margin", "p25": 0.45, "p50": 0.65, "p75": 0.80, "p90": 0.90, "sample_size": 180},
            {"sector": "fintech", "stage": "seed", "metric_name": "employee_count", "p25": 5.0, "p50": 12.0, "p75": 20.0, "p90": 35.0, "sample_size": 200},
            
            # Series A FinTech
            {"sector": "fintech", "stage": "series_a", "metric_name": "revenue_growth_rate", "p25": 0.25, "p50": 0.45, "p75": 0.70, "p90": 1.0, "sample_size": 120},
            {"sector": "fintech", "stage": "series_a", "metric_name": "customer_acquisition_cost", "p25": 80.0, "p50": 150.0, "p75": 250.0, "p90": 400.0, "sample_size": 115},
            {"sector": "fintech", "stage": "series_a", "metric_name": "monthly_recurring_revenue", "p25": 100000.0, "p50": 300000.0, "p75": 600000.0, "p90": 1200000.0, "sample_size": 100},
            
            # HealthTech benchmarks
            {"sector": "healthtech", "stage": "seed", "metric_name": "revenue_growth_rate", "p25": 0.20, "p50": 0.35, "p75": 0.55, "p90": 0.80, "sample_size": 80},
            {"sector": "healthtech", "stage": "seed", "metric_name": "customer_acquisition_cost", "p25": 100.0, "p50": 200.0, "p75": 350.0, "p90": 500.0, "sample_size": 75},
            {"sector": "healthtech", "stage": "seed", "metric_name": "gross_margin", "p25": 0.50, "p50": 0.70, "p75": 0.85, "p90": 0.95, "sample_size": 90},
            
            # AI/ML benchmarks
            {"sector": "ai_ml", "stage": "seed", "metric_name": "revenue_growth_rate", "p25": 0.30, "p50": 0.50, "p75": 0.80, "p90": 1.20, "sample_size": 60},
            {"sector": "ai_ml", "stage": "seed", "metric_name": "customer_acquisition_cost", "p25": 75.0, "p50": 150.0, "p75": 300.0, "p90": 500.0, "sample_size": 55},
            {"sector": "ai_ml", "stage": "seed", "metric_name": "gross_margin", "p25": 0.60, "p50": 0.75, "p75": 0.85, "p90": 0.95, "sample_size": 65},
            
            # EdTech benchmarks
            {"sector": "edtech", "stage": "seed", "metric_name": "revenue_growth_rate", "p25": 0.25, "p50": 0.40, "p75": 0.65, "p90": 0.90, "sample_size": 70},
            {"sector": "edtech", "stage": "seed", "metric_name": "customer_acquisition_cost", "p25": 30.0, "p50": 80.0, "p75": 150.0, "p90": 250.0, "sample_size": 68},
            {"sector": "edtech", "stage": "seed", "metric_name": "gross_margin", "p25": 0.55, "p50": 0.70, "p75": 0.80, "p90": 0.90, "sample_size": 72},
            
            # SaaS benchmarks
            {"sector": "saas", "stage": "seed", "metric_name": "revenue_growth_rate", "p25": 0.20, "p50": 0.35, "p75": 0.60, "p90": 0.85, "sample_size": 200},
            {"sector": "saas", "stage": "seed", "metric_name": "customer_acquisition_cost", "p25": 60.0, "p50": 120.0, "p75": 200.0, "p90": 300.0, "sample_size": 195},
            {"sector": "saas", "stage": "seed", "metric_name": "monthly_recurring_revenue", "p25": 20000.0, "p50": 60000.0, "p75": 120000.0, "p90": 250000.0, "sample_size": 180},
            {"sector": "saas", "stage": "seed", "metric_name": "gross_margin", "p25": 0.65, "p50": 0.75, "p75": 0.85, "p90": 0.92, "sample_size": 210},
        ]
        
        # Insert data into BigQuery (in a real implementation)
        # For demo purposes, we'll store this in memory
        self.benchmark_cache = benchmark_data
        logger.info(f"Created {len(benchmark_data)} benchmark records")
    
    async def get_sector_benchmarks(
        self, 
        sector: str, 
        stage: str, 
        metrics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get benchmark data for a specific sector and stage"""
        
        try:
            # Filter benchmark data
            filtered_benchmarks = [
                b for b in self.benchmark_cache 
                if b["sector"] == sector.lower() and b["stage"] == stage.lower()
            ]
            
            if metrics:
                filtered_benchmarks = [
                    b for b in filtered_benchmarks 
                    if b["metric_name"] in metrics
                ]
            
            return filtered_benchmarks
            
        except Exception as e:
            logger.error(f"Failed to get sector benchmarks: {e}")
            return []
    
    async def benchmark_startup(
        self, 
        startup_metrics: Dict[str, float], 
        sector: str, 
        stage: str
    ) -> List[BenchmarkData]:
        """Benchmark a startup against sector peers"""
        
        try:
            # Get sector benchmarks
            sector_benchmarks = await self.get_sector_benchmarks(sector, stage)
            
            benchmark_results = []
            
            for metric_name, startup_value in startup_metrics.items():
                # Find matching benchmark
                benchmark = next(
                    (b for b in sector_benchmarks if b["metric_name"] == metric_name),
                    None
                )
                
                if benchmark:
                    # Calculate percentile rank
                    percentile_rank = self._calculate_percentile_rank(
                        startup_value,
                        benchmark["p25"],
                        benchmark["p50"], 
                        benchmark["p75"],
                        benchmark["p90"]
                    )
                    
                    # Determine performance rating
                    performance_rating = self._get_performance_rating(percentile_rank)
                    
                    benchmark_results.append(BenchmarkData(
                        metric_name=metric_name.replace("_", " ").title(),
                        startup_value=startup_value,
                        sector_median=benchmark["p50"],
                        sector_p75=benchmark["p75"],
                        sector_p90=benchmark["p90"],
                        percentile_rank=percentile_rank,
                        performance_rating=performance_rating
                    ))
            
            return benchmark_results
            
        except Exception as e:
            logger.error(f"Startup benchmarking failed: {e}")
            return []
    
    def _calculate_percentile_rank(
        self, 
        value: float, 
        p25: float, 
        p50: float, 
        p75: float, 
        p90: float
    ) -> float:
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
    
    def _get_performance_rating(self, percentile_rank: float) -> str:
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
    
    async def get_market_trends(
        self, 
        sector: str, 
        metric: str, 
        time_period: str = "12m"
    ) -> Dict[str, Any]:
        """Get market trends for a sector and metric"""
        
        try:
            # Mock trend data (in real implementation, query historical data)
            base_values = {
                "revenue_growth_rate": {"q1": 0.25, "q2": 0.28, "q3": 0.30, "q4": 0.32},
                "customer_acquisition_cost": {"q1": 150.0, "q2": 145.0, "q3": 140.0, "q4": 135.0},
                "gross_margin": {"q1": 0.65, "q2": 0.67, "q3": 0.68, "q4": 0.70}
            }
            
            if metric not in base_values:
                metric = "revenue_growth_rate"  # Default
            
            trend_data = {
                "sector": sector,
                "metric": metric,
                "time_period": time_period,
                "trend_direction": "increasing" if metric != "customer_acquisition_cost" else "decreasing",
                "trend_strength": 0.75,
                "data_points": [
                    {"period": "2024-Q1", "median": base_values[metric]["q1"], "p75": base_values[metric]["q1"] * 1.6, "p90": base_values[metric]["q1"] * 2.4},
                    {"period": "2024-Q2", "median": base_values[metric]["q2"], "p75": base_values[metric]["q2"] * 1.6, "p90": base_values[metric]["q2"] * 2.4},
                    {"period": "2024-Q3", "median": base_values[metric]["q3"], "p75": base_values[metric]["q3"] * 1.6, "p90": base_values[metric]["q3"] * 2.4},
                    {"period": "2024-Q4", "median": base_values[metric]["q4"], "p75": base_values[metric]["q4"] * 1.6, "p90": base_values[metric]["q4"] * 2.4}
                ],
                "insights": [
                    f"{metric.replace('_', ' ').title()} has {'increased' if metric != 'customer_acquisition_cost' else 'decreased'} over the past year",
                    "Top performers are pulling ahead of the median",
                    f"Market conditions favor {'growth' if metric != 'customer_acquisition_cost' else 'efficiency'}-focused startups"
                ]
            }
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Market trends analysis failed: {e}")
            return {}
    
    async def compare_multiple_startups(
        self, 
        startups_data: List[Dict[str, Any]], 
        sector: str, 
        stage: str
    ) -> Dict[str, Any]:
        """Compare multiple startups against each other and sector benchmarks"""
        
        try:
            comparison_results = {}
            sector_benchmarks = await self.get_sector_benchmarks(sector, stage)
            
            # Common metrics to compare
            common_metrics = ["revenue_growth_rate", "customer_acquisition_cost", "gross_margin", "employee_count"]
            
            for startup in startups_data:
                startup_id = startup.get("startup_id", "unknown")
                startup_metrics = startup.get("metrics", {})
                
                # Benchmark against sector
                benchmarks = await self.benchmark_startup(startup_metrics, sector, stage)
                
                comparison_results[startup_id] = {
                    "startup_name": startup.get("name", "Unknown"),
                    "benchmarks": [b.dict() for b in benchmarks],
                    "overall_percentile": np.mean([b.percentile_rank for b in benchmarks]) if benchmarks else 0.5,
                    "metrics": startup_metrics
                }
            
            # Calculate rankings
            sorted_startups = sorted(
                comparison_results.items(),
                key=lambda x: x[1]["overall_percentile"],
                reverse=True
            )
            
            # Add rankings
            for i, (startup_id, data) in enumerate(sorted_startups):
                comparison_results[startup_id]["rank"] = i + 1
                comparison_results[startup_id]["percentile_rank"] = data["overall_percentile"]
            
            return {
                "sector": sector,
                "stage": stage,
                "total_startups": len(startups_data),
                "comparison_results": comparison_results,
                "sector_benchmarks": sector_benchmarks,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Multi-startup comparison failed: {e}")
            return {}
    
    async def get_peer_analysis(
        self, 
        startup_metrics: Dict[str, float], 
        sector: str, 
        stage: str
    ) -> Dict[str, Any]:
        """Get detailed peer analysis for a startup"""
        
        try:
            benchmarks = await self.benchmark_startup(startup_metrics, sector, stage)
            
            # Calculate overall performance
            overall_percentile = np.mean([b.percentile_rank for b in benchmarks]) if benchmarks else 0.5
            
            # Determine strengths and weaknesses
            strengths = [b for b in benchmarks if b.percentile_rank >= 0.75]
            weaknesses = [b for b in benchmarks if b.percentile_rank <= 0.25]
            
            peer_analysis = {
                "sector": sector,
                "stage": stage,
                "overall_percentile": overall_percentile,
                "overall_rank_estimate": max(1, int((1 - overall_percentile) * 100)),  # Estimated rank out of 100
                "strengths": [
                    {
                        "metric": s.metric_name,
                        "percentile": s.percentile_rank,
                        "rating": s.performance_rating,
                        "value": s.startup_value
                    } for s in strengths
                ],
                "weaknesses": [
                    {
                        "metric": w.metric_name,
                        "percentile": w.percentile_rank,
                        "rating": w.performance_rating,
                        "value": w.startup_value
                    } for w in weaknesses
                ],
                "improvement_opportunities": [
                    f"Focus on improving {w.metric_name} - currently at {w.percentile_rank:.0%} percentile"
                    for w in weaknesses
                ],
                "competitive_advantages": [
                    f"Strong {s.metric_name} performance - top {(1-s.percentile_rank)*100:.0f}% in sector"
                    for s in strengths
                ]
            }
            
            return peer_analysis
            
        except Exception as e:
            logger.error(f"Peer analysis failed: {e}")
            return {}


# Global benchmarking service instance
benchmarking_service = BenchmarkingService()
