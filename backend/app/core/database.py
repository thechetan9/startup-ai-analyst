"""
Database initialization and connection management
"""

from google.cloud import bigquery, firestore
from google.cloud.exceptions import NotFound
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and initialization"""
    
    def __init__(self):
        self.bigquery_client = None
        self.firestore_client = None
    
    async def init_bigquery(self):
        """Initialize BigQuery client and create datasets/tables if needed"""
        try:
            self.bigquery_client = bigquery.Client(project=settings.google_cloud_project_id)
            
            # Create dataset if it doesn't exist
            dataset_id = f"{settings.google_cloud_project_id}.{settings.bigquery_dataset_id}"
            try:
                self.bigquery_client.get_dataset(dataset_id)
                logger.info(f"Dataset {dataset_id} already exists")
            except NotFound:
                dataset = bigquery.Dataset(dataset_id)
                dataset.location = settings.google_cloud_region
                dataset = self.bigquery_client.create_dataset(dataset, timeout=30)
                logger.info(f"Created dataset {dataset_id}")
            
            # Create tables
            await self._create_bigquery_tables()
            
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery: {e}")
            raise
    
    async def init_firestore(self):
        """Initialize Firestore client"""
        try:
            self.firestore_client = firestore.Client(project=settings.firebase_project_id)
            logger.info("Firestore client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            raise
    
    async def _create_bigquery_tables(self):
        """Create BigQuery tables with proper schemas"""
        
        # Startups table schema
        startups_schema = [
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sector", "STRING"),
            bigquery.SchemaField("stage", "STRING"),
            bigquery.SchemaField("founded_date", "DATE"),
            bigquery.SchemaField("location", "STRING"),
            bigquery.SchemaField("funding_raised", "FLOAT"),
            bigquery.SchemaField("valuation", "FLOAT"),
            bigquery.SchemaField("employee_count", "INTEGER"),
            bigquery.SchemaField("revenue", "FLOAT"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        # Analysis results table schema
        analysis_schema = [
            bigquery.SchemaField("analysis_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("startup_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("analysis_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("score", "FLOAT"),
            bigquery.SchemaField("insights", "JSON"),
            bigquery.SchemaField("risk_flags", "JSON"),
            bigquery.SchemaField("benchmarks", "JSON"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        # Benchmarks table schema
        benchmarks_schema = [
            bigquery.SchemaField("benchmark_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sector", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("stage", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("metric_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("metric_value", "FLOAT"),
            bigquery.SchemaField("percentile_25", "FLOAT"),
            bigquery.SchemaField("percentile_50", "FLOAT"),
            bigquery.SchemaField("percentile_75", "FLOAT"),
            bigquery.SchemaField("percentile_90", "FLOAT"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        tables_config = [
            (settings.bigquery_table_startups, startups_schema),
            (settings.bigquery_table_analysis, analysis_schema),
            (settings.bigquery_table_benchmarks, benchmarks_schema),
        ]
        
        for table_name, schema in tables_config:
            table_id = f"{settings.google_cloud_project_id}.{settings.bigquery_dataset_id}.{table_name}"
            try:
                self.bigquery_client.get_table(table_id)
                logger.info(f"Table {table_id} already exists")
            except NotFound:
                table = bigquery.Table(table_id, schema=schema)
                table = self.bigquery_client.create_table(table)
                logger.info(f"Created table {table_id}")


# Global database manager instance
db_manager = DatabaseManager()


async def init_db():
    """Initialize all database connections"""
    await db_manager.init_bigquery()
    await db_manager.init_firestore()


def get_bigquery_client():
    """Get BigQuery client"""
    return db_manager.bigquery_client


def get_firestore_client():
    """Get Firestore client"""
    return db_manager.firestore_client
