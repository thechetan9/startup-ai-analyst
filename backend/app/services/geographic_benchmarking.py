"""
Geographic & Advanced Benchmarking Service
Provides region-specific market data and cross-geographic comparisons
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class GeographicMarketData:
    """Geographic market data structure"""
    region: str
    country: str
    market_size_usd: float
    growth_rate: float
    startup_density: int
    funding_availability: str  # "high", "medium", "low"
    regulatory_environment: str  # "favorable", "neutral", "restrictive"
    talent_availability: str
    cost_of_operations: str  # "low", "medium", "high"
    currency_code: str
    economic_indicators: Dict[str, float]

@dataclass
class BenchmarkComparison:
    """Benchmark comparison result"""
    startup_metrics: Dict[str, float]
    regional_benchmarks: Dict[str, float]
    global_benchmarks: Dict[str, float]
    percentile_rankings: Dict[str, float]
    competitive_position: str
    regional_advantages: List[str]
    regional_challenges: List[str]

class GeographicBenchmarkingService:
    """Service for geographic and advanced benchmarking"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Regional market data
        self.regional_data = self._load_regional_data()
        
        # Currency conversion rates (mock - replace with real API)
        self.currency_rates = self._load_currency_rates()
    
    async def get_geographic_benchmarks(
        self,
        startup_data: Dict[str, Any],
        target_regions: List[str] = None
    ) -> Dict[str, BenchmarkComparison]:
        """Get geographic benchmarks for startup"""
        
        try:
            startup_region = self._detect_startup_region(startup_data)
            startup_sector = startup_data.get("sector", "Technology")
            
            # Default to comparing with major startup hubs
            if not target_regions:
                target_regions = ["North America", "Europe", "Asia-Pacific", "Global"]
            
            benchmarks = {}
            
            for region in target_regions:
                try:
                    comparison = await self._compare_with_region(
                        startup_data, 
                        startup_region,
                        region,
                        startup_sector
                    )
                    benchmarks[region] = comparison
                except Exception as e:
                    logger.error(f"Failed to benchmark against {region}: {e}")
                    continue
            
            return benchmarks
            
        except Exception as e:
            logger.error(f"Geographic benchmarking failed: {e}")
            return {}
    
    async def analyze_market_opportunity(
        self,
        startup_data: Dict[str, Any],
        expansion_regions: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze market opportunity in different regions"""
        
        try:
            startup_sector = startup_data.get("sector", "Technology")
            current_region = self._detect_startup_region(startup_data)
            
            opportunities = {}
            
            for region in expansion_regions:
                try:
                    regional_data = self.regional_data.get(region, {})
                    
                    # Calculate market opportunity score
                    opportunity_analysis = await self._analyze_regional_opportunity(
                        startup_data,
                        region,
                        startup_sector,
                        regional_data
                    )
                    
                    opportunities[region] = opportunity_analysis
                    
                except Exception as e:
                    logger.error(f"Failed to analyze opportunity in {region}: {e}")
                    continue
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Market opportunity analysis failed: {e}")
            return {}
    
    def calculate_currency_adjusted_metrics(
        self,
        metrics: Dict[str, float],
        from_currency: str,
        to_currency: str = "USD"
    ) -> Dict[str, float]:
        """Convert financial metrics between currencies"""
        
        try:
            if from_currency == to_currency:
                return metrics
            
            conversion_rate = self._get_conversion_rate(from_currency, to_currency)
            
            adjusted_metrics = {}
            financial_keys = ["revenue", "funding", "valuation", "burn_rate", "cac", "ltv"]
            
            for key, value in metrics.items():
                if any(fin_key in key.lower() for fin_key in financial_keys):
                    adjusted_metrics[key] = value * conversion_rate
                else:
                    adjusted_metrics[key] = value
            
            return adjusted_metrics
            
        except Exception as e:
            logger.error(f"Currency adjustment failed: {e}")
            return metrics
    
    async def _compare_with_region(
        self,
        startup_data: Dict[str, Any],
        startup_region: str,
        target_region: str,
        sector: str
    ) -> BenchmarkComparison:
        """Compare startup with regional benchmarks"""
        
        try:
            # Get startup metrics
            startup_metrics = self._extract_startup_metrics(startup_data)
            
            # Get regional benchmarks
            regional_benchmarks = await self._get_regional_benchmarks(target_region, sector)
            
            # Get global benchmarks for comparison
            global_benchmarks = await self._get_global_benchmarks(sector)
            
            # Calculate percentile rankings
            percentile_rankings = self._calculate_percentiles(
                startup_metrics,
                regional_benchmarks
            )
            
            # Determine competitive position
            competitive_position = self._determine_competitive_position(percentile_rankings)
            
            # Identify regional advantages and challenges
            regional_advantages, regional_challenges = await self._analyze_regional_factors(
                startup_data,
                target_region,
                startup_region
            )
            
            return BenchmarkComparison(
                startup_metrics=startup_metrics,
                regional_benchmarks=regional_benchmarks,
                global_benchmarks=global_benchmarks,
                percentile_rankings=percentile_rankings,
                competitive_position=competitive_position,
                regional_advantages=regional_advantages,
                regional_challenges=regional_challenges
            )
            
        except Exception as e:
            logger.error(f"Regional comparison failed: {e}")
            return self._create_empty_comparison()
    
    async def _analyze_regional_opportunity(
        self,
        startup_data: Dict[str, Any],
        region: str,
        sector: str,
        regional_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze market opportunity in specific region"""
        
        try:
            analysis_prompt = f"""
            Analyze the market opportunity for a {sector} startup in {region}:
            
            Startup Data: {json.dumps(startup_data, indent=2)[:1000]}
            Regional Data: {json.dumps(regional_data, indent=2)[:500]}
            
            Provide analysis as JSON:
            {{
                "market_size_score": 0-100,
                "competition_level": "low/medium/high",
                "regulatory_favorability": 0-100,
                "talent_availability": 0-100,
                "funding_accessibility": 0-100,
                "cost_efficiency": 0-100,
                "overall_opportunity_score": 0-100,
                "key_advantages": [],
                "key_challenges": [],
                "recommended_entry_strategy": "",
                "timeline_to_market": "months",
                "investment_required": "low/medium/high"
            }}
            """
            
            response = await self._query_gemini(analysis_prompt)
            return self._parse_json_response(response)
            
        except Exception as e:
            logger.error(f"Regional opportunity analysis failed: {e}")
            return {}
    
    async def _get_regional_benchmarks(self, region: str, sector: str) -> Dict[str, float]:
        """Get benchmark metrics for specific region and sector"""
        
        # Mock regional benchmarks - replace with real data
        regional_benchmarks = {
            "North America": {
                "Technology": {
                    "avg_revenue": 2500000,
                    "avg_funding": 8000000,
                    "avg_team_size": 25,
                    "avg_growth_rate": 0.45,
                    "avg_burn_rate": 150000,
                    "avg_runway_months": 18
                }
            },
            "Europe": {
                "Technology": {
                    "avg_revenue": 1800000,
                    "avg_funding": 5500000,
                    "avg_team_size": 20,
                    "avg_growth_rate": 0.35,
                    "avg_burn_rate": 100000,
                    "avg_runway_months": 20
                }
            },
            "Asia-Pacific": {
                "Technology": {
                    "avg_revenue": 1200000,
                    "avg_funding": 4000000,
                    "avg_team_size": 30,
                    "avg_growth_rate": 0.60,
                    "avg_burn_rate": 80000,
                    "avg_runway_months": 16
                }
            }
        }
        
        return regional_benchmarks.get(region, {}).get(sector, {})
    
    async def _get_global_benchmarks(self, sector: str) -> Dict[str, float]:
        """Get global benchmark metrics for sector"""
        
        # Mock global benchmarks
        global_benchmarks = {
            "Technology": {
                "avg_revenue": 2000000,
                "avg_funding": 6500000,
                "avg_team_size": 24,
                "avg_growth_rate": 0.42,
                "avg_burn_rate": 120000,
                "avg_runway_months": 18
            }
        }
        
        return global_benchmarks.get(sector, {})
    
    def _extract_startup_metrics(self, startup_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics from startup data"""
        
        financial_data = startup_data.get("financial_data", {})
        team_data = startup_data.get("team_data", {})
        
        return {
            "revenue": financial_data.get("revenue", 0),
            "funding": financial_data.get("total_funding", 0),
            "team_size": team_data.get("team_size", 0),
            "growth_rate": financial_data.get("growth_rate", 0),
            "burn_rate": financial_data.get("burn_rate", 0),
            "runway_months": financial_data.get("runway_months", 0)
        }
    
    def _calculate_percentiles(
        self,
        startup_metrics: Dict[str, float],
        benchmarks: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate percentile rankings against benchmarks"""
        
        percentiles = {}
        
        for metric, value in startup_metrics.items():
            benchmark_key = f"avg_{metric}"
            if benchmark_key in benchmarks and benchmarks[benchmark_key] > 0:
                # Simple percentile calculation (would use more sophisticated method with real data)
                ratio = value / benchmarks[benchmark_key]
                if ratio >= 1.5:
                    percentile = 90
                elif ratio >= 1.2:
                    percentile = 75
                elif ratio >= 0.8:
                    percentile = 50
                elif ratio >= 0.5:
                    percentile = 25
                else:
                    percentile = 10
                
                percentiles[metric] = percentile
            else:
                percentiles[metric] = 50  # Default median
        
        return percentiles

    def _determine_competitive_position(self, percentiles: Dict[str, float]) -> str:
        """Determine competitive position based on percentiles"""

        if not percentiles:
            return "Unknown"

        avg_percentile = sum(percentiles.values()) / len(percentiles)

        if avg_percentile >= 80:
            return "Market Leader"
        elif avg_percentile >= 60:
            return "Strong Performer"
        elif avg_percentile >= 40:
            return "Average Performer"
        elif avg_percentile >= 20:
            return "Below Average"
        else:
            return "Underperformer"

    async def _analyze_regional_factors(
        self,
        startup_data: Dict[str, Any],
        target_region: str,
        startup_region: str
    ) -> Tuple[List[str], List[str]]:
        """Analyze regional advantages and challenges"""

        try:
            analysis_prompt = f"""
            Compare the advantages and challenges of operating in {target_region} vs {startup_region}:

            Startup: {json.dumps(startup_data, indent=2)[:800]}

            Provide analysis as JSON:
            {{
                "advantages": ["advantage1", "advantage2", ...],
                "challenges": ["challenge1", "challenge2", ...]
            }}

            Consider:
            - Market access and size
            - Regulatory environment
            - Talent availability
            - Funding ecosystem
            - Cost of operations
            - Cultural factors
            """

            response = await self._query_gemini(analysis_prompt)
            result = self._parse_json_response(response)

            advantages = result.get("advantages", [])
            challenges = result.get("challenges", [])

            return advantages, challenges

        except Exception as e:
            logger.error(f"Regional factor analysis failed: {e}")
            return [], []

    def _detect_startup_region(self, startup_data: Dict[str, Any]) -> str:
        """Detect startup's primary region"""

        # Try to extract from various data fields
        location_fields = [
            startup_data.get("location", ""),
            startup_data.get("headquarters", ""),
            startup_data.get("country", ""),
            startup_data.get("region", "")
        ]

        location_text = " ".join(filter(None, location_fields)).lower()

        # Simple region detection
        if any(country in location_text for country in ["usa", "united states", "canada"]):
            return "North America"
        elif any(country in location_text for country in ["uk", "germany", "france", "spain", "italy", "netherlands"]):
            return "Europe"
        elif any(country in location_text for country in ["china", "japan", "singapore", "australia", "india"]):
            return "Asia-Pacific"
        elif any(country in location_text for country in ["brazil", "mexico", "argentina"]):
            return "Latin America"
        else:
            return "Unknown"

    def _load_regional_data(self) -> Dict[str, Dict[str, Any]]:
        """Load regional market data"""

        return {
            "North America": {
                "market_size_usd": 500000000000,  # $500B
                "growth_rate": 0.08,
                "startup_density": 15000,
                "funding_availability": "high",
                "regulatory_environment": "favorable",
                "talent_availability": "high",
                "cost_of_operations": "high",
                "currency_code": "USD"
            },
            "Europe": {
                "market_size_usd": 300000000000,  # $300B
                "growth_rate": 0.06,
                "startup_density": 12000,
                "funding_availability": "medium",
                "regulatory_environment": "neutral",
                "talent_availability": "high",
                "cost_of_operations": "medium",
                "currency_code": "EUR"
            },
            "Asia-Pacific": {
                "market_size_usd": 400000000000,  # $400B
                "growth_rate": 0.12,
                "startup_density": 20000,
                "funding_availability": "medium",
                "regulatory_environment": "mixed",
                "talent_availability": "high",
                "cost_of_operations": "low",
                "currency_code": "USD"
            }
        }

    def _load_currency_rates(self) -> Dict[str, float]:
        """Load currency conversion rates (mock data)"""

        return {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.75,
            "JPY": 110.0,
            "CNY": 6.5,
            "INR": 75.0,
            "CAD": 1.25,
            "AUD": 1.35
        }

    def _get_conversion_rate(self, from_currency: str, to_currency: str) -> float:
        """Get currency conversion rate"""

        try:
            from_rate = self.currency_rates.get(from_currency, 1.0)
            to_rate = self.currency_rates.get(to_currency, 1.0)

            # Convert to USD first, then to target currency
            usd_value = 1.0 / from_rate
            target_value = usd_value * to_rate

            return target_value

        except Exception as e:
            logger.error(f"Currency conversion failed: {e}")
            return 1.0

    def _create_empty_comparison(self) -> BenchmarkComparison:
        """Create empty benchmark comparison"""

        return BenchmarkComparison(
            startup_metrics={},
            regional_benchmarks={},
            global_benchmarks={},
            percentile_rankings={},
            competitive_position="Unknown",
            regional_advantages=[],
            regional_challenges=[]
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


# Global geographic benchmarking service instance
geographic_service = GeographicBenchmarkingService()
