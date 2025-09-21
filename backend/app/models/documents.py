"""
Document processing models and schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Types of documents that can be processed"""
    PITCH_DECK = "pitch_deck"
    FINANCIAL_STATEMENT = "financial_statement"
    BUSINESS_PLAN = "business_plan"
    CALL_TRANSCRIPT = "call_transcript"
    EMAIL = "email"
    FOUNDER_UPDATE = "founder_update"
    MARKET_RESEARCH = "market_research"
    LEGAL_DOCUMENT = "legal_document"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentUpload(BaseModel):
    """Model for document upload request"""
    startup_id: str = Field(..., description="Associated startup ID")
    document_type: DocumentType = Field(..., description="Type of document")
    filename: str = Field(..., description="Original filename")
    description: Optional[str] = Field(None, description="Document description")


class Document(BaseModel):
    """Document model"""
    document_id: str = Field(..., description="Unique document identifier")
    startup_id: str = Field(..., description="Associated startup ID")
    document_type: DocumentType = Field(..., description="Type of document")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Storage file path")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    description: Optional[str] = Field(None, description="Document description")
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.UPLOADED)
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    processed_at: Optional[datetime] = Field(None, description="Processing completion timestamp")
    
    class Config:
        from_attributes = True


class ExtractedContent(BaseModel):
    """Extracted content from document"""
    document_id: str = Field(..., description="Source document ID")
    raw_text: str = Field(..., description="Raw extracted text")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="Structured data extracted")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Document metadata")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Extraction confidence")


class PitchDeckData(BaseModel):
    """Structured data extracted from pitch deck"""
    company_name: Optional[str] = None
    tagline: Optional[str] = None
    problem_statement: Optional[str] = None
    solution_description: Optional[str] = None
    market_size: Optional[Dict[str, Any]] = None
    business_model: Optional[str] = None
    revenue_model: Optional[str] = None
    traction_metrics: Optional[Dict[str, Any]] = None
    financial_projections: Optional[Dict[str, Any]] = None
    team_info: Optional[List[Dict[str, str]]] = None
    funding_ask: Optional[Dict[str, Any]] = None
    use_of_funds: Optional[List[str]] = None
    competition_analysis: Optional[Dict[str, Any]] = None
    go_to_market_strategy: Optional[str] = None


class FinancialStatementData(BaseModel):
    """Structured data from financial statements"""
    period: Optional[str] = None
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_expenses: Optional[float] = None
    net_income: Optional[float] = None
    cash_flow: Optional[float] = None
    assets: Optional[float] = None
    liabilities: Optional[float] = None
    equity: Optional[float] = None
    key_metrics: Optional[Dict[str, float]] = None


class CallTranscriptData(BaseModel):
    """Structured data from call transcripts"""
    call_date: Optional[datetime] = None
    participants: Optional[List[str]] = None
    duration_minutes: Optional[int] = None
    key_topics: Optional[List[str]] = None
    action_items: Optional[List[str]] = None
    concerns_raised: Optional[List[str]] = None
    positive_signals: Optional[List[str]] = None
    questions_asked: Optional[List[str]] = None
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)


class EmailData(BaseModel):
    """Structured data from emails"""
    sender: Optional[str] = None
    recipients: Optional[List[str]] = None
    subject: Optional[str] = None
    sent_date: Optional[datetime] = None
    email_type: Optional[str] = None  # update, inquiry, pitch, etc.
    key_points: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    urgency_level: Optional[str] = None


class ProcessingResult(BaseModel):
    """Result of document processing"""
    document_id: str = Field(..., description="Processed document ID")
    processing_status: ProcessingStatus = Field(..., description="Processing status")
    extracted_content: Optional[ExtractedContent] = None
    structured_data: Optional[Dict[str, Any]] = None
    processing_errors: Optional[List[str]] = None
    processing_time_seconds: Optional[float] = None
    processed_at: datetime = Field(..., description="Processing completion timestamp")


class DocumentAnalysisRequest(BaseModel):
    """Request for document analysis"""
    document_ids: List[str] = Field(..., description="List of document IDs to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")
    custom_prompts: Optional[List[str]] = Field(None, description="Custom analysis prompts")
    include_benchmarking: bool = Field(default=True, description="Include benchmarking analysis")
    include_risk_assessment: bool = Field(default=True, description="Include risk assessment")


class DocumentAnalysisResult(BaseModel):
    """Result of document analysis"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    document_ids: List[str] = Field(..., description="Analyzed document IDs")
    startup_id: str = Field(..., description="Associated startup ID")
    
    # Analysis results
    key_insights: List[str] = Field(default_factory=list)
    extracted_metrics: Dict[str, Any] = Field(default_factory=dict)
    risk_indicators: List[str] = Field(default_factory=list)
    inconsistencies: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    
    # Confidence and quality scores
    overall_confidence: float = Field(..., ge=0, le=1)
    data_quality_score: float = Field(..., ge=0, le=1)
    completeness_score: float = Field(..., ge=0, le=1)
    
    created_at: datetime = Field(..., description="Analysis timestamp")
    
    class Config:
        from_attributes = True
