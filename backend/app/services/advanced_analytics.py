"""
Advanced Analytics & Reporting Dashboard Service
Generates comprehensive investor reports and analytics
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report structure"""
    report_id: str
    company_name: str
    generated_at: datetime
    executive_summary: Dict[str, Any]
    detailed_analysis: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    market_intelligence: Dict[str, Any]
    financial_projections: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    investment_recommendation: Dict[str, Any]
    appendices: Dict[str, Any]

@dataclass
class PortfolioAnalytics:
    """Portfolio-level analytics"""
    total_companies: int
    total_investment: float
    avg_score: float
    sector_distribution: Dict[str, int]
    stage_distribution: Dict[str, int]
    geographic_distribution: Dict[str, int]
    performance_metrics: Dict[str, float]
    risk_distribution: Dict[str, int]
    top_performers: List[Dict[str, Any]]
    underperformers: List[Dict[str, Any]]

class AdvancedAnalyticsService:
    """Service for advanced analytics and reporting"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
    
    async def generate_comprehensive_report(
        self,
        startup_data: Dict[str, Any],
        risk_assessment: Dict[str, Any] = None,
        market_intelligence: Dict[str, Any] = None,
        custom_scoring: Dict[str, Any] = None,
        geographic_benchmarks: Dict[str, Any] = None
    ) -> AnalyticsReport:
        """Generate comprehensive investment report"""
        
        try:
            company_name = startup_data.get("company_name", "Unknown Company")
            report_id = f"RPT_{company_name.replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate each section of the report
            executive_summary = await self._generate_executive_summary(
                startup_data, risk_assessment, custom_scoring
            )
            
            detailed_analysis = await self._generate_detailed_analysis(
                startup_data, market_intelligence, geographic_benchmarks
            )
            
            risk_assessment_section = self._format_risk_assessment(risk_assessment)
            
            market_intelligence_section = self._format_market_intelligence(market_intelligence)
            
            financial_projections = await self._generate_financial_projections(startup_data)
            
            competitive_analysis = await self._generate_competitive_analysis(
                startup_data, market_intelligence
            )
            
            investment_recommendation = await self._generate_investment_recommendation(
                startup_data, risk_assessment, custom_scoring
            )
            
            appendices = self._generate_appendices(
                startup_data, risk_assessment, market_intelligence
            )
            
            return AnalyticsReport(
                report_id=report_id,
                company_name=company_name,
                generated_at=datetime.utcnow(),
                executive_summary=executive_summary,
                detailed_analysis=detailed_analysis,
                risk_assessment=risk_assessment_section,
                market_intelligence=market_intelligence_section,
                financial_projections=financial_projections,
                competitive_analysis=competitive_analysis,
                investment_recommendation=investment_recommendation,
                appendices=appendices
            )
            
        except Exception as e:
            logger.error(f"Comprehensive report generation failed: {e}")
            return self._create_empty_report(startup_data.get("company_name", "Unknown"))
    
    async def generate_portfolio_analytics(
        self,
        portfolio_companies: List[Dict[str, Any]]
    ) -> PortfolioAnalytics:
        """Generate portfolio-level analytics"""
        
        try:
            if not portfolio_companies:
                return self._create_empty_portfolio_analytics()
            
            # Calculate basic metrics
            total_companies = len(portfolio_companies)
            total_investment = sum(
                company.get("investment_amount", 0) for company in portfolio_companies
            )
            
            scores = [company.get("overall_score", 0) for company in portfolio_companies]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # Analyze distributions
            sector_distribution = self._analyze_distribution(
                portfolio_companies, "sector"
            )
            
            stage_distribution = self._analyze_distribution(
                portfolio_companies, "stage"
            )
            
            geographic_distribution = self._analyze_distribution(
                portfolio_companies, "region"
            )
            
            # Calculate performance metrics
            performance_metrics = self._calculate_portfolio_performance(portfolio_companies)
            
            # Analyze risk distribution
            risk_distribution = self._analyze_risk_distribution(portfolio_companies)
            
            # Identify top and underperformers
            top_performers = self._identify_top_performers(portfolio_companies)
            underperformers = self._identify_underperformers(portfolio_companies)
            
            return PortfolioAnalytics(
                total_companies=total_companies,
                total_investment=total_investment,
                avg_score=avg_score,
                sector_distribution=sector_distribution,
                stage_distribution=stage_distribution,
                geographic_distribution=geographic_distribution,
                performance_metrics=performance_metrics,
                risk_distribution=risk_distribution,
                top_performers=top_performers,
                underperformers=underperformers
            )
            
        except Exception as e:
            logger.error(f"Portfolio analytics generation failed: {e}")
            return self._create_empty_portfolio_analytics()
    
    async def generate_trend_analysis(
        self,
        historical_data: List[Dict[str, Any]],
        time_period: str = "12_months"
    ) -> Dict[str, Any]:
        """Generate trend analysis over time"""
        
        try:
            trend_prompt = f"""
            Analyze trends in this startup investment data over {time_period}:
            
            Historical Data: {json.dumps(historical_data[:50], indent=2)[:2000]}
            
            Provide trend analysis as JSON:
            {{
                "overall_trends": {{
                    "investment_volume": "increasing/stable/decreasing",
                    "average_scores": "improving/stable/declining",
                    "sector_shifts": []
                }},
                "sector_trends": {{}},
                "geographic_trends": {{}},
                "risk_trends": {{
                    "overall_risk_level": "increasing/stable/decreasing",
                    "common_risk_factors": []
                }},
                "market_trends": {{
                    "hot_sectors": [],
                    "emerging_opportunities": [],
                    "declining_areas": []
                }},
                "predictions": {{
                    "next_quarter_outlook": "",
                    "recommended_focus_areas": []
                }}
            }}
            """
            
            response = await self._query_gemini(trend_prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {}
    
    async def _generate_executive_summary(
        self,
        startup_data: Dict[str, Any],
        risk_assessment: Dict[str, Any] = None,
        custom_scoring: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate executive summary section"""
        
        try:
            summary_prompt = f"""
            Generate an executive summary for this startup investment analysis:
            
            Startup Data: {json.dumps(startup_data, indent=2)[:1500]}
            Risk Assessment: {json.dumps(risk_assessment or {}, indent=2)[:500]}
            Custom Scoring: {json.dumps(custom_scoring or {}, indent=2)[:500]}
            
            Provide as JSON:
            {{
                "investment_thesis": "",
                "key_strengths": [],
                "key_concerns": [],
                "overall_recommendation": "STRONG INVEST/INVEST/HOLD/PASS",
                "confidence_level": "high/medium/low",
                "investment_amount_range": "",
                "expected_timeline": "",
                "key_milestones": [],
                "next_steps": []
            }}
            """
            
            response = await self._query_gemini(summary_prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return {}
    
    async def _generate_detailed_analysis(
        self,
        startup_data: Dict[str, Any],
        market_intelligence: Dict[str, Any] = None,
        geographic_benchmarks: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate detailed analysis section"""
        
        try:
            analysis_prompt = f"""
            Generate detailed analysis for this startup:
            
            Startup Data: {json.dumps(startup_data, indent=2)[:1200]}
            Market Intelligence: {json.dumps(market_intelligence or {}, indent=2)[:400]}
            Geographic Benchmarks: {json.dumps(geographic_benchmarks or {}, indent=2)[:400]}
            
            Provide as JSON:
            {{
                "business_model_analysis": {{
                    "model_type": "",
                    "revenue_streams": [],
                    "unit_economics": {{}},
                    "scalability_assessment": ""
                }},
                "market_analysis": {{
                    "market_size": "",
                    "growth_potential": "",
                    "competitive_landscape": "",
                    "market_timing": ""
                }},
                "team_analysis": {{
                    "founder_quality": "",
                    "team_composition": "",
                    "experience_assessment": "",
                    "execution_capability": ""
                }},
                "product_analysis": {{
                    "product_differentiation": "",
                    "technology_assessment": "",
                    "product_market_fit": "",
                    "development_stage": ""
                }},
                "financial_analysis": {{
                    "revenue_trajectory": "",
                    "burn_rate_analysis": "",
                    "funding_requirements": "",
                    "path_to_profitability": ""
                }}
            }}
            """
            
            response = await self._query_gemini(analysis_prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Detailed analysis generation failed: {e}")
            return {}
    
    def _format_risk_assessment(self, risk_assessment: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format risk assessment for report"""
        
        if not risk_assessment:
            return {"overall_risk": "Unknown", "risk_factors": [], "mitigation_strategies": []}
        
        return {
            "overall_risk_level": risk_assessment.get("overall_risk_score", "Unknown"),
            "critical_risks": risk_assessment.get("critical_risks", []),
            "medium_risks": risk_assessment.get("medium_risks", []),
            "risk_mitigation": risk_assessment.get("mitigation_strategies", []),
            "risk_monitoring": risk_assessment.get("monitoring_recommendations", [])
        }
    
    def _format_market_intelligence(self, market_intelligence: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format market intelligence for report"""
        
        if not market_intelligence:
            return {"market_sentiment": "Unknown", "competitive_position": "Unknown"}
        
        return {
            "market_sentiment": market_intelligence.get("news_sentiment", 0),
            "hiring_trends": market_intelligence.get("hiring_trends", {}),
            "funding_landscape": market_intelligence.get("funding_activity", {}),
            "competitive_intelligence": market_intelligence.get("competitive_landscape", {}),
            "market_signals": market_intelligence.get("market_signals", [])
        }

    async def _generate_financial_projections(self, startup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial projections"""

        try:
            projection_prompt = f"""
            Generate 3-year financial projections for this startup:

            Current Data: {json.dumps(startup_data.get('financial_data', {}), indent=2)[:800]}

            Provide as JSON:
            {{
                "revenue_projections": {{
                    "year_1": 0,
                    "year_2": 0,
                    "year_3": 0
                }},
                "growth_assumptions": {{
                    "year_1_growth": 0,
                    "year_2_growth": 0,
                    "year_3_growth": 0
                }},
                "expense_projections": {{
                    "year_1": 0,
                    "year_2": 0,
                    "year_3": 0
                }},
                "funding_requirements": {{
                    "total_needed": 0,
                    "runway_extension": 0,
                    "use_of_funds": []
                }},
                "key_assumptions": [],
                "sensitivity_analysis": {{
                    "best_case": {{}},
                    "worst_case": {{}},
                    "most_likely": {{}}
                }}
            }}
            """

            response = await self._query_gemini(projection_prompt)
            return self._parse_json_response(response)

        except Exception as e:
            logger.error(f"Financial projections generation failed: {e}")
            return {}

    async def _generate_competitive_analysis(
        self,
        startup_data: Dict[str, Any],
        market_intelligence: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate competitive analysis"""

        try:
            competitive_prompt = f"""
            Generate competitive analysis for this startup:

            Startup: {json.dumps(startup_data, indent=2)[:1000]}
            Market Data: {json.dumps(market_intelligence or {}, indent=2)[:500]}

            Provide as JSON:
            {{
                "competitive_positioning": "",
                "direct_competitors": [],
                "indirect_competitors": [],
                "competitive_advantages": [],
                "competitive_threats": [],
                "market_share_potential": "",
                "differentiation_strategy": "",
                "competitive_moats": []
            }}
            """

            response = await self._query_gemini(competitive_prompt)
            return self._parse_json_response(response)

        except Exception as e:
            logger.error(f"Competitive analysis generation failed: {e}")
            return {}

    async def _generate_investment_recommendation(
        self,
        startup_data: Dict[str, Any],
        risk_assessment: Dict[str, Any] = None,
        custom_scoring: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate investment recommendation"""

        try:
            recommendation_prompt = f"""
            Generate investment recommendation for this startup:

            Startup: {json.dumps(startup_data, indent=2)[:1000]}
            Risk Assessment: {json.dumps(risk_assessment or {}, indent=2)[:400]}
            Scoring: {json.dumps(custom_scoring or {}, indent=2)[:400]}

            Provide as JSON:
            {{
                "recommendation": "STRONG INVEST/INVEST/HOLD/PASS",
                "investment_rationale": "",
                "suggested_investment_amount": 0,
                "valuation_assessment": "",
                "terms_recommendations": [],
                "due_diligence_priorities": [],
                "success_metrics": [],
                "exit_strategy": "",
                "timeline_expectations": ""
            }}
            """

            response = await self._query_gemini(recommendation_prompt)
            return self._parse_json_response(response)

        except Exception as e:
            logger.error(f"Investment recommendation generation failed: {e}")
            return {}

    def _generate_appendices(
        self,
        startup_data: Dict[str, Any],
        risk_assessment: Dict[str, Any] = None,
        market_intelligence: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate report appendices"""

        return {
            "data_sources": [
                "Company pitch deck",
                "Financial statements",
                "Market research",
                "Public data sources",
                "AI analysis"
            ],
            "methodology": {
                "scoring_framework": "Custom weighted scoring",
                "risk_assessment": "Multi-factor risk analysis",
                "market_analysis": "Public data integration",
                "benchmarking": "Sector and geographic comparisons"
            },
            "assumptions": [
                "Market growth rates based on industry averages",
                "Financial projections assume current trajectory",
                "Risk assessment based on available data",
                "Competitive analysis based on public information"
            ],
            "disclaimers": [
                "Analysis based on available information at time of report",
                "Projections are estimates and actual results may vary",
                "Investment decisions should consider additional factors",
                "Past performance does not guarantee future results"
            ]
        }

    def _analyze_distribution(self, companies: List[Dict[str, Any]], field: str) -> Dict[str, int]:
        """Analyze distribution of a field across companies"""

        distribution = {}
        for company in companies:
            value = company.get(field, "Unknown")
            distribution[value] = distribution.get(value, 0) + 1

        return distribution

    def _calculate_portfolio_performance(self, companies: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate portfolio performance metrics"""

        if not companies:
            return {}

        scores = [company.get("overall_score", 0) for company in companies]
        investments = [company.get("investment_amount", 0) for company in companies]

        return {
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "median_score": sorted(scores)[len(scores)//2] if scores else 0,
            "total_investment": sum(investments),
            "avg_investment": sum(investments) / len(investments) if investments else 0,
            "score_variance": self._calculate_variance(scores),
            "high_performers_pct": len([s for s in scores if s >= 80]) / len(scores) * 100 if scores else 0
        }

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of values"""

        if not values:
            return 0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def _analyze_risk_distribution(self, companies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze risk distribution across portfolio"""

        risk_levels = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}

        for company in companies:
            risk_level = company.get("risk_level", "Medium")
            if risk_level in risk_levels:
                risk_levels[risk_level] += 1

        return risk_levels

    def _identify_top_performers(self, companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify top performing companies"""

        sorted_companies = sorted(
            companies,
            key=lambda x: x.get("overall_score", 0),
            reverse=True
        )

        return sorted_companies[:5]  # Top 5

    def _identify_underperformers(self, companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify underperforming companies"""

        sorted_companies = sorted(
            companies,
            key=lambda x: x.get("overall_score", 0)
        )

        return sorted_companies[:3]  # Bottom 3

    def _create_empty_report(self, company_name: str) -> AnalyticsReport:
        """Create empty report when generation fails"""

        return AnalyticsReport(
            report_id=f"RPT_ERROR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            company_name=company_name,
            generated_at=datetime.utcnow(),
            executive_summary={},
            detailed_analysis={},
            risk_assessment={},
            market_intelligence={},
            financial_projections={},
            competitive_analysis={},
            investment_recommendation={},
            appendices={}
        )

    def _create_empty_portfolio_analytics(self) -> PortfolioAnalytics:
        """Create empty portfolio analytics"""

        return PortfolioAnalytics(
            total_companies=0,
            total_investment=0.0,
            avg_score=0.0,
            sector_distribution={},
            stage_distribution={},
            geographic_distribution={},
            performance_metrics={},
            risk_distribution={},
            top_performers=[],
            underperformers=[]
        )

    async def _query_gemini(self, prompt: str) -> str:
        """Query Gemini AI model"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            return "{}"

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from AI"""
        try:
            import json
            import re

            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {}
        except Exception as e:
            logger.error(f"JSON parsing failed: {e}")
            return {}


# Global advanced analytics service instance
analytics_service = AdvancedAnalyticsService()
