"""
Configuration settings for the AI Startup Analyst platform
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "AI Startup Analyst"
    debug: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google Cloud
    google_cloud_project_id: str
    google_application_credentials: Optional[str] = None
    google_cloud_region: str = "us-central1"
    
    # Gemini API
    gemini_api_key: str
    
    # BigQuery
    bigquery_dataset_id: str = "startup_analytics"
    bigquery_table_startups: str = "startups"
    bigquery_table_benchmarks: str = "benchmarks"
    bigquery_table_analysis: str = "analysis_results"
    
    # Firebase
    firebase_project_id: str
    firebase_api_key: str
    firebase_auth_domain: str
    firebase_storage_bucket: str
    
    # Cloud Storage
    gcs_bucket_name: str = "startup-documents"
    gcs_bucket_processed: str = "startup-processed-data"
    
    # External APIs
    crunchbase_api_key: Optional[str] = None
    pitchbook_api_key: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
