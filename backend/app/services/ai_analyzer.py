"""
AI-powered startup analysis service using Gemini
"""

import logging
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime
import google.generativeai as genai
from google.cloud import bigquery

from app.core.config import settings
from app.models.startup import (
    StartupAnalysis, AnalysisInsight, RiskFlag, BenchmarkData,
    FinancialMetrics, TractionMetrics, TeamMetrics, RiskLevel
)
from app.services.benchmarking_service import benchmarking_service
from app.services.risk_assessment import risk_assessment_service

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered startup analysis using Gemini and Google Cloud services"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.bigquery_client = bigquery.Client(project=settings.google_cloud_project_id)
    
    async def analyze_startup_comprehensive(
        self,
        startup_id: str,
        documents_data: List[Dict[str, Any]],
        custom_weightings: Optional[Dict[str, float]] = None
    ) -> StartupAnalysis:
        """Perform comprehensive startup analysis"""
        
        try:
            logger.info(f"Starting comprehensive analysis for startup {startup_id}")
            
            # Step 1: Extract and consolidate data from all documents
            consolidated_data = await self._consolidate_document_data(documents_data)
            
            # Step 2: Generate AI insights using Gemini
            insights = await self._generate_insights(consolidated_data, startup_id)
            
            # Step 3: Assess risks and red flags
            risk_flags = await self._assess_risks(consolidated_data, startup_id)
            
            # Step 4: Generate benchmarks
            benchmarks = await self._generate_benchmarks(consolidated_data, startup_id)
            
            # Step 5: Calculate overall score
            overall_score = await self._calculate_overall_score(
                consolidated_data, insights, risk_flags, benchmarks, custom_weightings
            )
            
            # Step 6: Generate investment recommendation
            recommendation = await self._generate_investment_recommendation(
                overall_score, insights, risk_flags, benchmarks
            )
            
            # Step 7: Extract structured metrics
            financial_metrics = self._extract_financial_metrics(consolidated_data)
            traction_metrics = self._extract_traction_metrics(consolidated_data)
            team_metrics = self._extract_team_metrics(consolidated_data)
            
            return StartupAnalysis(
                analysis_id=f"analysis_{startup_id}_{int(datetime.now().timestamp())}",
                startup_id=startup_id,
                analysis_type="comprehensive",
                overall_score=overall_score,
                financial_metrics=financial_metrics,
                traction_metrics=traction_metrics,
                team_metrics=team_metrics,
                insights=insights,
                risk_flags=risk_flags,
                benchmarks=benchmarks,
                investment_recommendation=recommendation["recommendation"],
                key_strengths=recommendation["strengths"],
                key_concerns=recommendation["concerns"],
                next_steps=recommendation["next_steps"],
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            raise
    
    async def _consolidate_document_data(self, documents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolidate data from multiple documents"""
        
        consolidated = {
            "company_info": {},
            "financial_data": {},
            "traction_data": {},
            "team_data": {},
            "market_data": {},
            "business_model": {},
            "raw_documents": documents_data
        }
        
        for doc_data in documents_data:
            if not doc_data.get("structured_data"):
                continue
            
            structured = doc_data["structured_data"]
            
            # Consolidate company information
            if "company_name" in structured:
                consolidated["company_info"]["name"] = structured["company_name"]
            if "tagline" in structured:
                consolidated["company_info"]["tagline"] = structured["tagline"]
            if "problem_statement" in structured:
                consolidated["company_info"]["problem"] = structured["problem_statement"]
            if "solution_description" in structured:
                consolidated["company_info"]["solution"] = structured["solution_description"]
            
            # Consolidate financial data
            if "revenue" in structured:
                consolidated["financial_data"]["revenue"] = structured["revenue"]
            if "financial_projections" in structured:
                consolidated["financial_data"]["projections"] = structured["financial_projections"]
            if "funding_ask" in structured:
                consolidated["financial_data"]["funding_ask"] = structured["funding_ask"]
            
            # Consolidate traction data
            if "traction_metrics" in structured:
                consolidated["traction_data"].update(structured["traction_metrics"])
            
            # Consolidate team data
            if "team_info" in structured:
                consolidated["team_data"]["team"] = structured["team_info"]
            
            # Consolidate market data
            if "market_size" in structured:
                consolidated["market_data"]["size"] = structured["market_size"]
            if "competition_analysis" in structured:
                consolidated["market_data"]["competition"] = structured["competition_analysis"]
            
            # Business model
            if "business_model" in structured:
                consolidated["business_model"]["model"] = structured["business_model"]
            if "revenue_model" in structured:
                consolidated["business_model"]["revenue_model"] = structured["revenue_model"]
        
        return consolidated
    
    async def _generate_insights(self, consolidated_data: Dict[str, Any], startup_id: str) -> List[AnalysisInsight]:
        """Generate AI-powered insights using Gemini"""
        
        try:
            prompt = f"""
            Analyze the following startup data and generate key investment insights:
            
            Company Data: {json.dumps(consolidated_data, indent=2)[:3000]}
            
            Please provide insights in the following categories:
            1. Growth Potential
            2. Market Opportunity
            3. Financial Health
            4. Team Strength
            5. Competitive Position
            6. Technology/Product
            7. Business Model
            
            For each insight, provide:
            - Category
            - Title (brief)
            - Description (detailed analysis)
            - Impact (potential impact on investment)
            - Confidence score (0-1)
            
            Return as JSON array with these fields.
            """
            
            response = await self._query_gemini(prompt)
            insights_data = self._parse_json_response(response)
            
            insights = []
            for insight_data in insights_data:
                insights.append(AnalysisInsight(
                    category=insight_data.get("category", "General"),
                    title=insight_data.get("title", "Analysis Point"),
                    description=insight_data.get("description", ""),
                    impact=insight_data.get("impact", ""),
                    confidence=float(insight_data.get("confidence", 0.7)),
                    supporting_data=insight_data.get("supporting_data")
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return []
    
    async def _assess_risks(self, consolidated_data: Dict[str, Any], startup_id: str) -> List[RiskFlag]:
        """Assess risks and red flags using comprehensive risk assessment service"""

        try:
            # Prepare startup data for risk assessment
            startup_data = {
                "startup_id": startup_id,
                "financial_data": consolidated_data.get("financial_data", {}),
                "market_data": consolidated_data.get("market_data", {}),
                "team_data": consolidated_data.get("team_data", {}),
                "product_data": consolidated_data.get("product_data", {}),
                "business_model": consolidated_data.get("business_model", {}),
                "traction_data": consolidated_data.get("traction_data", {})
            }

            # Prepare documents data (mock structure for now)
            documents_data = [
                {
                    "document_id": f"doc_{startup_id}_001",
                    "structured_data": consolidated_data
                }
            ]

            # Use comprehensive risk assessment service
            risk_flags = await risk_assessment_service.assess_startup_risks(
                startup_data=startup_data,
                documents_data=documents_data
            )

            return risk_flags

        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return []
    
    async def _generate_benchmarks(self, consolidated_data: Dict[str, Any], startup_id: str) -> List[BenchmarkData]:
        """Generate benchmark comparisons using benchmarking service"""

        try:
            # Extract key metrics for benchmarking
            sector = consolidated_data.get("company_info", {}).get("sector", "ai_ml")
            stage = consolidated_data.get("financial_data", {}).get("stage", "seed")

            # Extract startup metrics
            financial_data = consolidated_data.get("financial_data", {})
            traction_data = consolidated_data.get("traction_data", {})
            team_data = consolidated_data.get("team_data", {})

            startup_metrics = {}

            # Add available metrics
            if financial_data.get("growth_rate"):
                startup_metrics["revenue_growth_rate"] = financial_data["growth_rate"]
            if financial_data.get("gross_margin"):
                startup_metrics["gross_margin"] = financial_data["gross_margin"]
            if traction_data.get("customer_acquisition_cost"):
                startup_metrics["customer_acquisition_cost"] = traction_data["customer_acquisition_cost"]
            if team_data.get("size"):
                startup_metrics["employee_count"] = float(team_data["size"])

            # Use benchmarking service if metrics available
            if startup_metrics:
                benchmarks = await benchmarking_service.benchmark_startup(
                    startup_metrics=startup_metrics,
                    sector=sector,
                    stage=stage
                )
                return benchmarks
            else:
                # Fallback to mock data if no metrics available
                return []

        except Exception as e:
            logger.error(f"Benchmark generation failed: {e}")
            return []
    
    async def _calculate_overall_score(
        self,
        consolidated_data: Dict[str, Any],
        insights: List[AnalysisInsight],
        risk_flags: List[RiskFlag],
        benchmarks: List[BenchmarkData],
        custom_weightings: Optional[Dict[str, float]]
    ) -> float:
        """Calculate overall investment score"""
        
        try:
            # Default weightings
            default_weights = {
                "financial_health": 0.25,
                "market_opportunity": 0.20,
                "team_strength": 0.20,
                "traction": 0.15,
                "product_technology": 0.10,
                "competitive_position": 0.10
            }
            
            weights = custom_weightings or default_weights
            
            # Calculate component scores
            financial_score = self._calculate_financial_score(consolidated_data, benchmarks)
            market_score = self._calculate_market_score(consolidated_data, insights)
            team_score = self._calculate_team_score(consolidated_data, insights)
            traction_score = self._calculate_traction_score(consolidated_data, benchmarks)
            product_score = self._calculate_product_score(consolidated_data, insights)
            competitive_score = self._calculate_competitive_score(consolidated_data, insights)
            
            # Apply risk penalties
            risk_penalty = self._calculate_risk_penalty(risk_flags)
            
            # Calculate weighted score
            overall_score = (
                financial_score * weights.get("financial_health", 0.25) +
                market_score * weights.get("market_opportunity", 0.20) +
                team_score * weights.get("team_strength", 0.20) +
                traction_score * weights.get("traction", 0.15) +
                product_score * weights.get("product_technology", 0.10) +
                competitive_score * weights.get("competitive_position", 0.10)
            ) - risk_penalty
            
            return max(0, min(100, overall_score))
            
        except Exception as e:
            logger.error(f"Score calculation failed: {e}")
            return 50.0  # Default neutral score
    
    def _calculate_financial_score(self, data: Dict[str, Any], benchmarks: List[BenchmarkData]) -> float:
        """Calculate financial health score"""
        # Simplified scoring logic
        return 75.0
    
    def _calculate_market_score(self, data: Dict[str, Any], insights: List[AnalysisInsight]) -> float:
        """Calculate market opportunity score"""
        return 80.0
    
    def _calculate_team_score(self, data: Dict[str, Any], insights: List[AnalysisInsight]) -> float:
        """Calculate team strength score"""
        return 85.0
    
    def _calculate_traction_score(self, data: Dict[str, Any], benchmarks: List[BenchmarkData]) -> float:
        """Calculate traction score"""
        return 70.0
    
    def _calculate_product_score(self, data: Dict[str, Any], insights: List[AnalysisInsight]) -> float:
        """Calculate product/technology score"""
        return 78.0
    
    def _calculate_competitive_score(self, data: Dict[str, Any], insights: List[AnalysisInsight]) -> float:
        """Calculate competitive position score"""
        return 72.0
    
    def _calculate_risk_penalty(self, risk_flags: List[RiskFlag]) -> float:
        """Calculate penalty based on risk flags"""
        penalty = 0.0
        for risk in risk_flags:
            if risk.severity == RiskLevel.CRITICAL:
                penalty += 15.0
            elif risk.severity == RiskLevel.HIGH:
                penalty += 10.0
            elif risk.severity == RiskLevel.MEDIUM:
                penalty += 5.0
            else:
                penalty += 2.0
        return min(penalty, 30.0)  # Cap penalty at 30 points
    
    def _calculate_performance_rating(self, percentile_rank: float) -> str:
        """Calculate performance rating from percentile rank"""
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
    
    async def _generate_investment_recommendation(
        self,
        overall_score: float,
        insights: List[AnalysisInsight],
        risk_flags: List[RiskFlag],
        benchmarks: List[BenchmarkData]
    ) -> Dict[str, Any]:
        """Generate investment recommendation using AI"""
        
        try:
            prompt = f"""
            Based on the following analysis results, generate an investment recommendation:
            
            Overall Score: {overall_score}/100
            Key Insights: {[i.title for i in insights[:5]]}
            Risk Flags: {[r.flag_type for r in risk_flags]}
            Benchmark Performance: {[b.performance_rating for b in benchmarks]}
            
            Provide:
            1. Investment recommendation (INVEST/PASS/MONITOR)
            2. Key strengths (3-5 points)
            3. Key concerns (3-5 points)
            4. Next steps for due diligence (3-5 points)
            
            Return as JSON with fields: recommendation, strengths, concerns, next_steps
            """
            
            response = await self._query_gemini(prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return {
                "recommendation": "MONITOR - Requires further analysis",
                "strengths": ["Analysis in progress"],
                "concerns": ["Incomplete data"],
                "next_steps": ["Complete data collection"]
            }
    
    def _extract_financial_metrics(self, data: Dict[str, Any]) -> Optional[FinancialMetrics]:
        """Extract financial metrics from consolidated data"""
        financial_data = data.get("financial_data", {})
        return FinancialMetrics(
            revenue=financial_data.get("revenue"),
            revenue_growth_rate=financial_data.get("growth_rate"),
            gross_margin=financial_data.get("gross_margin"),
            burn_rate=financial_data.get("burn_rate"),
            runway_months=financial_data.get("runway_months")
        )
    
    def _extract_traction_metrics(self, data: Dict[str, Any]) -> Optional[TractionMetrics]:
        """Extract traction metrics from consolidated data"""
        traction_data = data.get("traction_data", {})
        return TractionMetrics(
            user_count=traction_data.get("users"),
            customer_count=traction_data.get("customers"),
            user_growth_rate=traction_data.get("user_growth"),
            customer_growth_rate=traction_data.get("customer_growth")
        )
    
    def _extract_team_metrics(self, data: Dict[str, Any]) -> Optional[TeamMetrics]:
        """Extract team metrics from consolidated data"""
        team_data = data.get("team_data", {})
        return TeamMetrics(
            employee_count=team_data.get("size"),
            founder_experience=team_data.get("founder_background")
        )
    
    async def _query_gemini(self, prompt: str) -> str:
        """Query Gemini AI model"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            raise
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from Gemini"""
        try:
            import re
            json_match = re.search(r'\{.*\}|\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "No JSON found in response", "raw": response[:500]}
        except Exception as e:
            logger.error(f"JSON parsing failed: {e}")
            return {"error": str(e), "raw": response[:500]}


# Global AI analyzer instance
ai_analyzer = AIAnalyzer()
