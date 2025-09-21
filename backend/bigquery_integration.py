"""
Google BigQuery Integration for Startup Analytics
Provides sector benchmarking, trend analysis, and investment insights
"""

import os
from typing import Dict, List, Any, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime, timedelta
import json

class BigQueryService:
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.dataset_id = os.getenv('BIGQUERY_DATASET_ID', 'startup_analytics')

        try:
            # Try to use service account key file if available
            service_account_path = 'my-project-genai-464305-firebase-adminsdk-fbsvc-fa154c5947.json'
            if os.path.exists(service_account_path):
                credentials = service_account.Credentials.from_service_account_file(service_account_path)
                self.client = bigquery.Client(project=self.project_id, credentials=credentials)
                print(f"✅ BigQuery initialized with service account for project: {self.project_id}")
            else:
                # Fallback to default credentials (for local development or Cloud Run with default service account)
                self.client = bigquery.Client(project=self.project_id)
                print(f"✅ BigQuery initialized with default credentials for project: {self.project_id}")

            self.dataset_ref = self.client.dataset(self.dataset_id)
        except Exception as e:
            print(f"⚠️ BigQuery not available: {e}")
            self.client = None

    async def _ensure_table_exists(self, table_id: str):
        """Ensure dataset and table exist, create if they don't"""
        try:
            # Create dataset if it doesn't exist
            try:
                self.client.get_dataset(self.dataset_ref)
                print(f"✅ Dataset {self.dataset_id} exists")
            except Exception:
                dataset = bigquery.Dataset(self.dataset_ref)
                dataset.location = "US"
                dataset = self.client.create_dataset(dataset, timeout=30)
                print(f"✅ Created dataset {self.dataset_id}")

            # Create table if it doesn't exist
            try:
                table = self.client.get_table(table_id)
                print(f"✅ Table analysis_results exists")
            except Exception:
                # Define complete table schema with all required fields
                schema = [
                    # Basic analysis fields
                    bigquery.SchemaField("analysis_id", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("company_name", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("sector", "STRING"),
                    bigquery.SchemaField("score", "INTEGER"),
                    bigquery.SchemaField("recommendation", "STRING"),
                    bigquery.SchemaField("analysis_text", "STRING"),

                    # Financial metrics
                    bigquery.SchemaField("revenue", "FLOAT"),
                    bigquery.SchemaField("growth_rate", "FLOAT"),
                    bigquery.SchemaField("funding", "FLOAT"),

                    # Document metadata
                    bigquery.SchemaField("document_count", "INTEGER"),
                    bigquery.SchemaField("file_types", "STRING"),
                    bigquery.SchemaField("analysis_timestamp", "TIMESTAMP", mode="REQUIRED"),
                    bigquery.SchemaField("confidence_score", "FLOAT"),

                    # Analysis content fields (for popup display)
                    bigquery.SchemaField("key_strengths", "STRING", mode="REPEATED"),
                    bigquery.SchemaField("main_concerns", "STRING", mode="REPEATED"),
                    bigquery.SchemaField("executive_summary", "STRING"),

                    # Scoring breakdown
                    bigquery.SchemaField("market_opportunity_score", "FLOAT"),
                    bigquery.SchemaField("team_quality_score", "FLOAT"),
                    bigquery.SchemaField("product_innovation_score", "FLOAT"),
                    bigquery.SchemaField("financial_potential_score", "FLOAT"),
                    bigquery.SchemaField("execution_capability_score", "FLOAT"),
                ]

                table = bigquery.Table(table_id, schema=schema)
                table = self.client.create_table(table)
                print(f"✅ Created table analysis_results")

        except Exception as e:
            print(f"⚠️ Error ensuring table exists: {e}")
            raise
    
    async def store_analysis_result(self, analysis_data: Dict[str, Any]) -> bool:
        """Store analysis result in BigQuery for future benchmarking"""
        if not self.client:
            return False

        try:
            table_id = f"{self.project_id}.{self.dataset_id}.analysis_results"

            # Ensure dataset and table exist
            await self._ensure_table_exists(table_id)

            # Prepare data for BigQuery
            company_name = analysis_data.get('company_name', analysis_data.get('companyName', ''))
            sector = analysis_data.get('sector', analysis_data.get('sector_benchmarks', {}).get('detected_sector', 'Unknown'))

            print(f"🔍 DEBUG BigQuery: company_name = '{company_name}'")
            print(f"🔍 DEBUG BigQuery: sector = '{sector}'")

            # Generate analysis_id if not provided
            analysis_id = analysis_data.get('id') or analysis_data.get('document_id') or analysis_data.get('analysis_id')
            if not analysis_id:
                import uuid
                analysis_id = f"analysis-{int(datetime.utcnow().timestamp() * 1000)}-{str(uuid.uuid4())[:8]}"
                print(f"🔍 Generated new analysis_id: {analysis_id}")

            # Extract financial metrics with debug logging - try both flattened and nested formats
            extracted_metrics = analysis_data.get('extracted_metrics', {})
            print(f"🔍 DEBUG BigQuery: extracted_metrics = {extracted_metrics}")

            # Try flattened fields first (from backend analysis), then nested (from frontend)
            revenue_raw = analysis_data.get('revenue') or extracted_metrics.get('revenue')
            growth_rate_raw = analysis_data.get('growth_rate') or extracted_metrics.get('growth_rate')
            funding_raw = analysis_data.get('funding') or extracted_metrics.get('funding')

            print(f"🔍 DEBUG BigQuery: revenue_raw = '{revenue_raw}' (flattened: {analysis_data.get('revenue')}, nested: {extracted_metrics.get('revenue')})")
            print(f"🔍 DEBUG BigQuery: growth_rate_raw = '{growth_rate_raw}' (flattened: {analysis_data.get('growth_rate')}, nested: {extracted_metrics.get('growth_rate')})")
            print(f"🔍 DEBUG BigQuery: funding_raw = '{funding_raw}' (flattened: {analysis_data.get('funding')}, nested: {extracted_metrics.get('funding')})")

            # Extract analysis content fields with comprehensive fallbacks
            key_strengths = analysis_data.get('key_strengths', [])
            main_concerns = analysis_data.get('main_concerns', [])
            executive_summary = analysis_data.get('executive_summary', '')
            scoring_breakdown = analysis_data.get('scoring_breakdown', {})

            # If structured_data exists, extract from there as fallback
            structured_data = analysis_data.get('structured_data', {})
            if not key_strengths and structured_data.get('key_strengths'):
                key_strengths = structured_data.get('key_strengths', [])
            if not main_concerns and structured_data.get('main_concerns'):
                main_concerns = structured_data.get('main_concerns', [])
            if not executive_summary and structured_data.get('executive_summary'):
                executive_summary = structured_data.get('executive_summary', '')
            if not scoring_breakdown and structured_data.get('scoring_breakdown'):
                scoring_breakdown = structured_data.get('scoring_breakdown', {})

            # Extract individual scoring fields (frontend sends these directly)
            market_opportunity_score = analysis_data.get('market_opportunity_score', 0) or scoring_breakdown.get('market_opportunity', 0)
            team_quality_score = analysis_data.get('team_quality_score', 0) or scoring_breakdown.get('team_quality', 0)
            product_innovation_score = analysis_data.get('product_innovation_score', 0) or scoring_breakdown.get('product_innovation', 0)
            financial_potential_score = analysis_data.get('financial_potential_score', 0) or scoring_breakdown.get('financial_potential', 0)
            execution_capability_score = analysis_data.get('execution_capability_score', 0) or scoring_breakdown.get('execution_capability', 0)

            print(f"🔍 DEBUG BigQuery Storage:")
            print(f"  - key_strengths: {key_strengths}")
            print(f"  - main_concerns: {main_concerns}")
            print(f"  - executive_summary: {executive_summary[:100]}...")
            print(f"  - scoring_breakdown: {scoring_breakdown}")
            print(f"  - individual scores: market={market_opportunity_score}, team={team_quality_score}, product={product_innovation_score}, financial={financial_potential_score}, execution={execution_capability_score}")

            row_data = {
                'analysis_id': analysis_id,
                'company_name': company_name,
                'sector': sector,
                'score': analysis_data.get('score', 0),
                'recommendation': analysis_data.get('recommendation', ''),
                'analysis_text': analysis_data.get('analysis_text', '')[:10000],  # Store full analysis (up to 10k chars)
                'revenue': self._extract_numeric_value(revenue_raw),
                'growth_rate': self._extract_numeric_value(growth_rate_raw),
                'funding': self._extract_numeric_value(funding_raw),
                'document_count': analysis_data.get('document_count', 0),
                'file_types': json.dumps(analysis_data.get('file_types', [])),
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'confidence_score': analysis_data.get('confidence_score', 0.8),
                # Analysis content fields
                'key_strengths': key_strengths if isinstance(key_strengths, list) else [],
                'main_concerns': main_concerns if isinstance(main_concerns, list) else [],
                'executive_summary': executive_summary,
                'market_opportunity_score': float(market_opportunity_score),
                'team_quality_score': float(team_quality_score),
                'product_innovation_score': float(product_innovation_score),
                'financial_potential_score': float(financial_potential_score),
                'execution_capability_score': float(execution_capability_score),
            }

            print(f"🔍 DEBUG BigQuery: Final values - revenue={row_data['revenue']}, growth_rate={row_data['growth_rate']}, funding={row_data['funding']}")
            
            # Insert row
            table = self.client.get_table(table_id)
            errors = self.client.insert_rows_json(table, [row_data])
            
            if not errors:
                print(f"✅ Analysis stored in BigQuery: {analysis_data.get('company_name')}")
                return True
            else:
                print(f"❌ BigQuery insert errors: {errors}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to store in BigQuery: {e}")
            return False
    
    async def get_sector_benchmarks(self, sector: str) -> Dict[str, Any]:
        """Get sector benchmarks from BigQuery"""
        if not self.client:
            return self._get_mock_benchmarks(sector)
        
        try:
            query = f"""
            SELECT 
                AVG(score) as avg_score,
                AVG(revenue) as avg_revenue,
                AVG(growth_rate) as avg_growth,
                COUNT(*) as sample_size,
                COUNTIF(recommendation = 'INVEST') as invest_count,
                COUNTIF(recommendation = 'HOLD') as hold_count,
                COUNTIF(recommendation = 'DO_NOT_INVEST') as reject_count
            FROM `{self.project_id}.{self.dataset_id}.analysis_results`
            WHERE sector = @sector
            AND DATE(analysis_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("sector", "STRING", sector)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return {
                    'sector': sector,
                    'avg_score': float(row.avg_score) if row.avg_score else 50.0,
                    'avg_revenue': float(row.avg_revenue) if row.avg_revenue else 0,
                    'avg_growth': float(row.avg_growth) if row.avg_growth else 0,
                    'sample_size': int(row.sample_size),
                    'investment_rate': (row.invest_count / row.sample_size * 100) if row.sample_size > 0 else 0,
                    'data_source': 'BigQuery',
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            # If no data found, return mock data
            return self._get_mock_benchmarks(sector)
            
        except Exception as e:
            print(f"❌ BigQuery benchmark query failed: {e}")
            return self._get_mock_benchmarks(sector)
    
    async def get_trending_sectors(self) -> List[Dict[str, Any]]:
        """Get trending sectors based on recent analysis activity"""
        if not self.client:
            return self._get_mock_trends()
        
        try:
            query = f"""
            SELECT 
                sector,
                COUNT(*) as analysis_count,
                AVG(score) as avg_score,
                COUNTIF(recommendation = 'INVEST') as invest_count
            FROM `{self.project_id}.{self.dataset_id}.analysis_results`
            WHERE DATE(analysis_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)
            GROUP BY sector
            HAVING analysis_count >= 3
            ORDER BY analysis_count DESC, avg_score DESC
            LIMIT 10
            """
            
            query_job = self.client.query(query)
            results = query_job.result()
            
            trends = []
            for row in results:
                trends.append({
                    'sector': row.sector,
                    'analysis_count': int(row.analysis_count),
                    'avg_score': float(row.avg_score),
                    'invest_rate': (row.invest_count / row.analysis_count * 100),
                    'trend': 'hot' if row.analysis_count > 10 else 'warm'
                })
            
            return trends if trends else self._get_mock_trends()
            
        except Exception as e:
            print(f"❌ Trending sectors query failed: {e}")
            return self._get_mock_trends()
    
    async def get_similar_companies(self, company_name: str, sector: str, score_range: int = 10) -> List[Dict[str, Any]]:
        """Find similar companies based on sector and score"""
        if not self.client:
            return []
        
        try:
            query = f"""
            SELECT 
                company_name,
                score,
                recommendation,
                revenue,
                growth_rate,
                analysis_timestamp
            FROM `{self.project_id}.{self.dataset_id}.analysis_results`
            WHERE sector = @sector
            AND company_name != @company_name
            AND ABS(score - @target_score) <= @score_range
            ORDER BY ABS(score - @target_score) ASC
            LIMIT 5
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("sector", "STRING", sector),
                    bigquery.ScalarQueryParameter("company_name", "STRING", company_name),
                    bigquery.ScalarQueryParameter("target_score", "INT64", 75),  # Default score
                    bigquery.ScalarQueryParameter("score_range", "INT64", score_range)
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            similar_companies = []
            for row in results:
                similar_companies.append({
                    'company_name': row.company_name,
                    'score': int(row.score),
                    'recommendation': row.recommendation,
                    'revenue': float(row.revenue) if row.revenue else 0,
                    'growth_rate': float(row.growth_rate) if row.growth_rate else 0,
                    'analyzed_date': row.analysis_timestamp.strftime('%Y-%m-%d') if row.analysis_timestamp else ''
                })
            
            return similar_companies
            
        except Exception as e:
            print(f"❌ Similar companies query failed: {e}")
            return []
    
    def _extract_numeric_value(self, value: Any) -> Optional[float]:
        """Extract numeric value from string or return None"""
        if not value:
            return None
        
        try:
            # Remove common currency symbols and text
            clean_value = str(value).replace('$', '').replace(',', '').replace('%', '')
            clean_value = ''.join(c for c in clean_value if c.isdigit() or c == '.')
            return float(clean_value) if clean_value else None
        except:
            return None
    
    def _get_mock_benchmarks(self, sector: str) -> Dict[str, Any]:
        """Mock benchmarks when BigQuery is not available"""
        mock_data = {
            'Tech': {'avg_score': 72, 'avg_revenue': 2500000, 'avg_growth': 45},
            'FinTech': {'avg_score': 68, 'avg_revenue': 1800000, 'avg_growth': 38},
            'HealthTech': {'avg_score': 65, 'avg_revenue': 1200000, 'avg_growth': 42},
            'EdTech': {'avg_score': 63, 'avg_revenue': 800000, 'avg_growth': 35}
        }
        
        base_data = mock_data.get(sector, {'avg_score': 60, 'avg_revenue': 1000000, 'avg_growth': 30})
        
        return {
            'sector': sector,
            'avg_score': base_data['avg_score'],
            'avg_revenue': base_data['avg_revenue'],
            'avg_growth': base_data['avg_growth'],
            'sample_size': 25,
            'investment_rate': 35.0,
            'data_source': 'Mock Data',
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _get_mock_trends(self) -> List[Dict[str, Any]]:
        """Mock trending sectors"""
        return [
            {'sector': 'AI/ML', 'analysis_count': 45, 'avg_score': 75, 'invest_rate': 42, 'trend': 'hot'},
            {'sector': 'FinTech', 'analysis_count': 38, 'avg_score': 68, 'invest_rate': 35, 'trend': 'hot'},
            {'sector': 'HealthTech', 'analysis_count': 32, 'avg_score': 65, 'invest_rate': 38, 'trend': 'warm'},
            {'sector': 'EdTech', 'analysis_count': 28, 'avg_score': 63, 'invest_rate': 32, 'trend': 'warm'}
        ]

# Global instance
bigquery_service = BigQueryService()

async def store_analysis_in_bigquery(analysis_result: Dict[str, Any]) -> bool:
    """Store analysis result in BigQuery for benchmarking"""
    return await bigquery_service.store_analysis_result(analysis_result)

async def get_enhanced_sector_benchmarks(sector: str) -> Dict[str, Any]:
    """Get enhanced sector benchmarks from BigQuery"""
    return await bigquery_service.get_sector_benchmarks(sector)
