"""
Startup data models and schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class StartupStage(str, Enum):
    """Startup funding stages"""
    PRE_SEED = "pre_seed"
    SEED = "seed"
    SERIES_A = "series_a"
    SERIES_B = "series_b"
    SERIES_C = "series_c"
    SERIES_D_PLUS = "series_d_plus"
    IPO = "ipo"
    ACQUIRED = "acquired"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StartupBase(BaseModel):
    """Base startup model"""
    name: str = Field(..., description="Startup name")
    sector: Optional[str] = Field(None, description="Industry sector")
    stage: Optional[StartupStage] = Field(None, description="Funding stage")
    founded_date: Optional[date] = Field(None, description="Founded date")
    location: Optional[str] = Field(None, description="Headquarters location")
    description: Optional[str] = Field(None, description="Company description")


class StartupCreate(StartupBase):
    """Model for creating a new startup"""
    pass


class StartupUpdate(BaseModel):
    """Model for updating startup information"""
    name: Optional[str] = None
    sector: Optional[str] = None
    stage: Optional[StartupStage] = None
    founded_date: Optional[date] = None
    location: Optional[str] = None
    description: Optional[str] = None
    funding_raised: Optional[float] = None
    valuation: Optional[float] = None
    employee_count: Optional[int] = None
    revenue: Optional[float] = None


class Startup(StartupBase):
    """Complete startup model"""
    startup_id: str = Field(..., description="Unique startup identifier")
    funding_raised: Optional[float] = Field(None, description="Total funding raised")
    valuation: Optional[float] = Field(None, description="Current valuation")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    revenue: Optional[float] = Field(None, description="Annual revenue")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record update timestamp")
    
    class Config:
        from_attributes = True


class FinancialMetrics(BaseModel):
    """Financial metrics for a startup"""
    revenue: Optional[float] = None
    revenue_growth_rate: Optional[float] = None
    gross_margin: Optional[float] = None
    burn_rate: Optional[float] = None
    runway_months: Optional[int] = None
    ltv_cac_ratio: Optional[float] = None
    churn_rate: Optional[float] = None
    arr: Optional[float] = None  # Annual Recurring Revenue
    mrr: Optional[float] = None  # Monthly Recurring Revenue


class TractionMetrics(BaseModel):
    """Traction and growth metrics"""
    user_count: Optional[int] = None
    user_growth_rate: Optional[float] = None
    customer_count: Optional[int] = None
    customer_growth_rate: Optional[float] = None
    market_share: Optional[float] = None
    partnerships: Optional[int] = None
    product_launches: Optional[int] = None


class TeamMetrics(BaseModel):
    """Team and hiring metrics"""
    employee_count: Optional[int] = None
    employee_growth_rate: Optional[float] = None
    engineering_ratio: Optional[float] = None
    sales_ratio: Optional[float] = None
    founder_experience: Optional[str] = None
    key_hires: Optional[List[str]] = None


class RiskFlag(BaseModel):
    """Risk assessment flag"""
    flag_type: str = Field(..., description="Type of risk flag")
    severity: RiskLevel = Field(..., description="Risk severity level")
    description: str = Field(..., description="Risk description")
    evidence: Optional[str] = Field(None, description="Supporting evidence")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")


class BenchmarkData(BaseModel):
    """Benchmark comparison data"""
    metric_name: str = Field(..., description="Name of the metric")
    startup_value: Optional[float] = Field(None, description="Startup's value for this metric")
    sector_median: Optional[float] = Field(None, description="Sector median value")
    sector_p75: Optional[float] = Field(None, description="Sector 75th percentile")
    sector_p90: Optional[float] = Field(None, description="Sector 90th percentile")
    percentile_rank: Optional[float] = Field(None, description="Startup's percentile rank")
    performance_rating: Optional[str] = Field(None, description="Performance rating")


class AnalysisInsight(BaseModel):
    """Individual analysis insight"""
    category: str = Field(..., description="Insight category")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    impact: str = Field(..., description="Potential impact")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    supporting_data: Optional[Dict[str, Any]] = Field(None, description="Supporting data")


class StartupAnalysis(BaseModel):
    """Complete startup analysis result"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    startup_id: str = Field(..., description="Startup identifier")
    analysis_type: str = Field(..., description="Type of analysis performed")
    overall_score: float = Field(..., ge=0, le=100, description="Overall investment score")
    
    # Detailed metrics
    financial_metrics: Optional[FinancialMetrics] = None
    traction_metrics: Optional[TractionMetrics] = None
    team_metrics: Optional[TeamMetrics] = None
    
    # Analysis results
    insights: List[AnalysisInsight] = Field(default_factory=list)
    risk_flags: List[RiskFlag] = Field(default_factory=list)
    benchmarks: List[BenchmarkData] = Field(default_factory=list)
    
    # Recommendations
    investment_recommendation: str = Field(..., description="Investment recommendation")
    key_strengths: List[str] = Field(default_factory=list)
    key_concerns: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(..., description="Analysis timestamp")
    
    class Config:
        from_attributes = True
