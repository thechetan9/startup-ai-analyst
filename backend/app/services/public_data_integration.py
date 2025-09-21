"""
Public Data Integration Service
Integrates external data sources for comprehensive startup analysis
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class PublicDataInsight:
    """Public data insight structure"""
    source: str
    data_type: str
    content: Dict[str, Any]
    relevance_score: float
    timestamp: datetime
    confidence: float

@dataclass
class MarketIntelligence:
    """Market intelligence data structure"""
    company_name: str
    news_sentiment: float
    hiring_trends: Dict[str, Any]
    funding_activity: Dict[str, Any]
    competitive_landscape: Dict[str, Any]
    market_signals: List[str]
    risk_indicators: List[str]
    growth_indicators: List[str]

class PublicDataIntegrationService:
    """Service for integrating public data sources"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # API endpoints and configurations
        self.news_apis = {
            "google_news": "https://newsapi.org/v2/everything",
            "bing_news": "https://api.bing.microsoft.com/v7.0/news/search"
        }
        
        self.job_apis = {
            "linkedin": "https://api.linkedin.com/v2/jobs",
            "indeed": "https://api.indeed.com/ads/apisearch"
        }
        
        self.funding_apis = {
            "crunchbase": "https://api.crunchbase.com/api/v4/entities/organizations",
            "pitchbook": "https://api.pitchbook.com/v1/companies"
        }
    
    async def gather_market_intelligence(
        self, 
        company_name: str,
        company_domain: Optional[str] = None,
        sector: Optional[str] = None
    ) -> MarketIntelligence:
        """Gather comprehensive market intelligence for a company"""
        
        try:
            # Gather data from multiple sources in parallel
            tasks = [
                self._get_news_sentiment(company_name),
                self._get_hiring_trends(company_name, company_domain),
                self._get_funding_activity(company_name),
                self._get_competitive_landscape(company_name, sector),
                self._get_market_signals(company_name, sector)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            news_sentiment = results[0] if not isinstance(results[0], Exception) else 0.0
            hiring_trends = results[1] if not isinstance(results[1], Exception) else {}
            funding_activity = results[2] if not isinstance(results[2], Exception) else {}
            competitive_landscape = results[3] if not isinstance(results[3], Exception) else {}
            market_signals = results[4] if not isinstance(results[4], Exception) else []
            
            # Analyze for risk and growth indicators
            risk_indicators = await self._identify_public_risks(
                company_name, news_sentiment, hiring_trends, funding_activity
            )
            
            growth_indicators = await self._identify_growth_signals(
                company_name, hiring_trends, funding_activity, market_signals
            )
            
            return MarketIntelligence(
                company_name=company_name,
                news_sentiment=news_sentiment,
                hiring_trends=hiring_trends,
                funding_activity=funding_activity,
                competitive_landscape=competitive_landscape,
                market_signals=market_signals,
                risk_indicators=risk_indicators,
                growth_indicators=growth_indicators
            )
            
        except Exception as e:
            logger.error(f"Market intelligence gathering failed for {company_name}: {e}")
            return self._create_empty_intelligence(company_name)
    
    async def _get_news_sentiment(self, company_name: str) -> float:
        """Get news sentiment analysis for company"""
        
        try:
            # Search for recent news about the company
            news_articles = await self._search_news(company_name, days_back=30)
            
            if not news_articles:
                return 0.0
            
            # Analyze sentiment using AI
            combined_text = " ".join([
                article.get("title", "") + " " + article.get("description", "")
                for article in news_articles[:10]  # Limit to top 10 articles
            ])
            
            sentiment_prompt = f"""
            Analyze the overall sentiment of these news articles about {company_name}:
            
            {combined_text[:2000]}
            
            Return a sentiment score from -1.0 (very negative) to 1.0 (very positive).
            Consider:
            - Positive: funding, growth, partnerships, product launches, awards
            - Negative: layoffs, scandals, failures, legal issues, declining metrics
            
            Return only the decimal number.
            """
            
            response = await self._query_gemini(sentiment_prompt)
            
            # Extract sentiment score
            import re
            score_match = re.search(r'-?\d+\.?\d*', response)
            if score_match:
                return max(-1.0, min(1.0, float(score_match.group())))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"News sentiment analysis failed: {e}")
            return 0.0
    
    async def _get_hiring_trends(self, company_name: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Get hiring trends and job posting data"""
        
        try:
            # Search for job postings
            job_data = await self._search_job_postings(company_name, domain)
            
            if not job_data:
                return {}
            
            # Analyze hiring patterns
            analysis_prompt = f"""
            Analyze these job postings for {company_name} and extract hiring insights:
            
            Job Data: {json.dumps(job_data[:20])}  # Limit data size
            
            Return as JSON:
            {{
                "total_openings": 0,
                "departments_hiring": [],
                "seniority_levels": {{}},
                "growth_indicators": [],
                "hiring_velocity": "high/medium/low",
                "key_roles": [],
                "geographic_expansion": [],
                "skill_requirements": []
            }}
            """
            
            response = await self._query_gemini(analysis_prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Hiring trends analysis failed: {e}")
            return {}
    
    async def _get_funding_activity(self, company_name: str) -> Dict[str, Any]:
        """Get funding and investment activity data"""
        
        try:
            # Search for funding information
            funding_data = await self._search_funding_data(company_name)
            
            if not funding_data:
                return {}
            
            # Analyze funding patterns
            analysis_prompt = f"""
            Analyze this funding data for {company_name}:
            
            Funding Data: {json.dumps(funding_data)}
            
            Return as JSON:
            {{
                "total_funding": 0,
                "last_round": {{}},
                "funding_history": [],
                "investor_quality": "tier1/tier2/tier3",
                "funding_velocity": "fast/normal/slow",
                "valuation_trend": "increasing/stable/decreasing",
                "next_round_signals": []
            }}
            """
            
            response = await self._query_gemini(analysis_prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Funding activity analysis failed: {e}")
            return {}
    
    async def _get_competitive_landscape(self, company_name: str, sector: Optional[str] = None) -> Dict[str, Any]:
        """Get competitive landscape analysis"""
        
        try:
            # Search for competitors and market data
            competitive_data = await self._search_competitive_data(company_name, sector)
            
            analysis_prompt = f"""
            Analyze the competitive landscape for {company_name} in the {sector or 'technology'} sector:
            
            Competitive Data: {json.dumps(competitive_data)}
            
            Return as JSON:
            {{
                "direct_competitors": [],
                "indirect_competitors": [],
                "market_position": "leader/challenger/follower/niche",
                "competitive_advantages": [],
                "competitive_threats": [],
                "market_share_estimate": "high/medium/low",
                "differentiation_factors": []
            }}
            """
            
            response = await self._query_gemini(analysis_prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Competitive landscape analysis failed: {e}")
            return {}
    
    async def _get_market_signals(self, company_name: str, sector: Optional[str] = None) -> List[str]:
        """Get market signals and trends"""
        
        try:
            # Search for market trends and signals
            market_data = await self._search_market_trends(company_name, sector)
            
            analysis_prompt = f"""
            Identify key market signals and trends relevant to {company_name}:
            
            Market Data: {json.dumps(market_data)}
            
            Look for:
            - Industry growth trends
            - Technology adoption patterns
            - Regulatory changes
            - Consumer behavior shifts
            - Economic indicators
            
            Return as JSON array of strings: ["signal1", "signal2", ...]
            """
            
            response = await self._query_gemini(analysis_prompt)
            signals = self._parse_json_response(response)
            return signals if isinstance(signals, list) else []
            
        except Exception as e:
            logger.error(f"Market signals analysis failed: {e}")
            return []
    
    async def _search_news(self, company_name: str, days_back: int = 30) -> List[Dict[str, Any]]:
        """Search for news articles about the company"""
        
        # Mock implementation - replace with actual news API calls
        mock_articles = [
            {
                "title": f"{company_name} raises Series A funding",
                "description": f"{company_name} announces successful Series A round",
                "source": "TechCrunch",
                "published_at": datetime.utcnow().isoformat(),
                "url": f"https://techcrunch.com/{company_name.lower()}-funding"
            },
            {
                "title": f"{company_name} launches new product feature",
                "description": f"{company_name} introduces innovative new capabilities",
                "source": "VentureBeat",
                "published_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                "url": f"https://venturebeat.com/{company_name.lower()}-product"
            }
        ]
        
        return mock_articles
    
    async def _search_job_postings(self, company_name: str, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for job postings by the company"""
        
        # Mock implementation - replace with actual job API calls
        mock_jobs = [
            {
                "title": "Senior Software Engineer",
                "department": "Engineering",
                "location": "San Francisco, CA",
                "posted_date": datetime.utcnow().isoformat(),
                "seniority": "Senior",
                "skills": ["Python", "React", "AWS"]
            },
            {
                "title": "Product Manager",
                "department": "Product",
                "location": "Remote",
                "posted_date": (datetime.utcnow() - timedelta(days=3)).isoformat(),
                "seniority": "Mid",
                "skills": ["Product Strategy", "Analytics", "User Research"]
            }
        ]
        
        return mock_jobs

    async def _search_funding_data(self, company_name: str) -> List[Dict[str, Any]]:
        """Search for funding and investment data"""

        # Mock implementation - replace with actual funding API calls
        mock_funding = [
            {
                "round_type": "Series A",
                "amount": 5000000,
                "date": "2024-01-15",
                "investors": ["Sequoia Capital", "Andreessen Horowitz"],
                "valuation": 25000000
            },
            {
                "round_type": "Seed",
                "amount": 1000000,
                "date": "2023-06-10",
                "investors": ["Y Combinator", "First Round Capital"],
                "valuation": 8000000
            }
        ]

        return mock_funding

    async def _search_competitive_data(self, company_name: str, sector: Optional[str] = None) -> Dict[str, Any]:
        """Search for competitive landscape data"""

        # Mock implementation - replace with actual competitive intelligence APIs
        mock_competitive = {
            "competitors": [
                {"name": "Competitor A", "funding": 50000000, "employees": 200},
                {"name": "Competitor B", "funding": 30000000, "employees": 150}
            ],
            "market_size": 10000000000,
            "growth_rate": 0.25,
            "key_players": ["Market Leader", "Challenger 1", "Challenger 2"]
        }

        return mock_competitive

    async def _search_market_trends(self, company_name: str, sector: Optional[str] = None) -> Dict[str, Any]:
        """Search for market trends and signals"""

        # Mock implementation - replace with actual market data APIs
        mock_trends = {
            "industry_growth": 0.15,
            "technology_adoption": "accelerating",
            "regulatory_environment": "favorable",
            "consumer_sentiment": "positive",
            "economic_indicators": {
                "gdp_growth": 0.03,
                "unemployment": 0.04,
                "inflation": 0.025
            }
        }

        return mock_trends

    async def _identify_public_risks(
        self,
        company_name: str,
        news_sentiment: float,
        hiring_trends: Dict[str, Any],
        funding_activity: Dict[str, Any]
    ) -> List[str]:
        """Identify risk indicators from public data"""

        risks = []

        try:
            # News sentiment risks
            if news_sentiment < -0.3:
                risks.append("Negative media coverage and public sentiment")

            # Hiring trend risks
            hiring_velocity = hiring_trends.get("hiring_velocity", "medium")
            if hiring_velocity == "low" and hiring_trends.get("total_openings", 0) < 5:
                risks.append("Limited hiring activity may indicate growth constraints")

            # Funding risks
            last_round = funding_activity.get("last_round", {})
            if last_round:
                last_round_date = last_round.get("date", "")
                if last_round_date:
                    # Check if last funding was more than 18 months ago
                    try:
                        from datetime import datetime
                        last_date = datetime.fromisoformat(last_round_date.replace('Z', '+00:00'))
                        months_since = (datetime.utcnow() - last_date).days / 30
                        if months_since > 18:
                            risks.append("Extended period since last funding round")
                    except:
                        pass

            # Use AI to identify additional risks
            risk_prompt = f"""
            Based on this public data for {company_name}, identify potential risks:

            News Sentiment: {news_sentiment}
            Hiring Data: {json.dumps(hiring_trends)}
            Funding Data: {json.dumps(funding_activity)}

            Return as JSON array of risk strings: ["risk1", "risk2", ...]
            """

            response = await self._query_gemini(risk_prompt)
            ai_risks = self._parse_json_response(response)
            if isinstance(ai_risks, list):
                risks.extend(ai_risks)

        except Exception as e:
            logger.error(f"Public risk identification failed: {e}")

        return risks

    async def _identify_growth_signals(
        self,
        company_name: str,
        hiring_trends: Dict[str, Any],
        funding_activity: Dict[str, Any],
        market_signals: List[str]
    ) -> List[str]:
        """Identify growth indicators from public data"""

        growth_indicators = []

        try:
            # Hiring growth signals
            hiring_velocity = hiring_trends.get("hiring_velocity", "medium")
            if hiring_velocity == "high":
                growth_indicators.append("Aggressive hiring indicates rapid scaling")

            total_openings = hiring_trends.get("total_openings", 0)
            if total_openings > 20:
                growth_indicators.append("Large number of open positions suggests expansion")

            # Funding growth signals
            funding_velocity = funding_activity.get("funding_velocity", "normal")
            if funding_velocity == "fast":
                growth_indicators.append("Rapid funding rounds indicate strong investor interest")

            valuation_trend = funding_activity.get("valuation_trend", "stable")
            if valuation_trend == "increasing":
                growth_indicators.append("Increasing valuation trend shows strong performance")

            # Market signals
            positive_signals = [s for s in market_signals if any(
                keyword in s.lower() for keyword in ["growth", "expansion", "adoption", "demand"]
            )]
            growth_indicators.extend(positive_signals)

            # Use AI to identify additional growth signals
            growth_prompt = f"""
            Based on this public data for {company_name}, identify growth indicators:

            Hiring Data: {json.dumps(hiring_trends)}
            Funding Data: {json.dumps(funding_activity)}
            Market Signals: {json.dumps(market_signals)}

            Return as JSON array of growth indicator strings: ["indicator1", "indicator2", ...]
            """

            response = await self._query_gemini(growth_prompt)
            ai_growth = self._parse_json_response(response)
            if isinstance(ai_growth, list):
                growth_indicators.extend(ai_growth)

        except Exception as e:
            logger.error(f"Growth signal identification failed: {e}")

        return growth_indicators

    def _create_empty_intelligence(self, company_name: str) -> MarketIntelligence:
        """Create empty market intelligence object"""
        return MarketIntelligence(
            company_name=company_name,
            news_sentiment=0.0,
            hiring_trends={},
            funding_activity={},
            competitive_landscape={},
            market_signals=[],
            risk_indicators=[],
            growth_indicators=[]
        )

    async def _query_gemini(self, prompt: str) -> str:
        """Query Gemini AI model"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            return ""

    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON response from AI"""
        try:
            import json
            import re

            # Look for JSON in the response
            json_match = re.search(r'[\{\[].*[\}\]]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {}
        except Exception as e:
            logger.error(f"JSON parsing failed: {e}")
            return {}


# Global public data integration service instance
public_data_service = PublicDataIntegrationService()
