"""
Customizable Investment Scoring Framework
Allows investors to define custom scoring criteria and weightings
"""

import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)

class ScoringCriterion(Enum):
    """Available scoring criteria"""
    TEAM_QUALITY = "team_quality"
    MARKET_SIZE = "market_size"
    PRODUCT_INNOVATION = "product_innovation"
    TRACTION = "traction"
    BUSINESS_MODEL = "business_model"
    FINANCIAL_HEALTH = "financial_health"
    COMPETITIVE_ADVANTAGE = "competitive_advantage"
    SCALABILITY = "scalability"
    EXECUTION_CAPABILITY = "execution_capability"
    RISK_PROFILE = "risk_profile"

@dataclass
class ScoringWeight:
    """Scoring weight configuration"""
    criterion: ScoringCriterion
    weight: float  # 0.0 to 1.0
    importance: str  # "critical", "high", "medium", "low"
    custom_factors: List[str] = None

@dataclass
class InvestmentThesis:
    """Investment thesis configuration"""
    name: str
    description: str
    scoring_weights: List[ScoringWeight]
    sector_preferences: List[str]
    stage_preferences: List[str]
    minimum_score_threshold: float
    risk_tolerance: str  # "conservative", "moderate", "aggressive"

@dataclass
class CustomScore:
    """Custom scoring result"""
    overall_score: float
    criterion_scores: Dict[str, float]
    weighted_scores: Dict[str, float]
    recommendation: str
    confidence: float
    thesis_alignment: float

class CustomizableScoringService:
    """Service for customizable investment scoring"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Default investment theses
        self.default_theses = self._create_default_theses()
    
    def create_custom_thesis(
        self,
        name: str,
        description: str,
        scoring_preferences: Dict[str, Any],
        sector_focus: List[str] = None,
        stage_focus: List[str] = None
    ) -> InvestmentThesis:
        """Create a custom investment thesis"""
        
        try:
            # Convert preferences to scoring weights
            scoring_weights = []
            
            for criterion_name, config in scoring_preferences.items():
                try:
                    criterion = ScoringCriterion(criterion_name)
                    weight = float(config.get("weight", 0.1))
                    importance = config.get("importance", "medium")
                    custom_factors = config.get("custom_factors", [])
                    
                    scoring_weights.append(ScoringWeight(
                        criterion=criterion,
                        weight=weight,
                        importance=importance,
                        custom_factors=custom_factors
                    ))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Invalid scoring criterion {criterion_name}: {e}")
                    continue
            
            # Normalize weights to sum to 1.0
            total_weight = sum(w.weight for w in scoring_weights)
            if total_weight > 0:
                for weight in scoring_weights:
                    weight.weight = weight.weight / total_weight
            
            return InvestmentThesis(
                name=name,
                description=description,
                scoring_weights=scoring_weights,
                sector_preferences=sector_focus or [],
                stage_preferences=stage_focus or [],
                minimum_score_threshold=scoring_preferences.get("minimum_threshold", 60.0),
                risk_tolerance=scoring_preferences.get("risk_tolerance", "moderate")
            )
            
        except Exception as e:
            logger.error(f"Failed to create custom thesis: {e}")
            return self.default_theses["balanced"]
    
    async def calculate_custom_score(
        self,
        startup_data: Dict[str, Any],
        investment_thesis: InvestmentThesis,
        market_intelligence: Dict[str, Any] = None
    ) -> CustomScore:
        """Calculate custom score based on investment thesis"""
        
        try:
            # Calculate individual criterion scores
            criterion_scores = {}
            
            for weight_config in investment_thesis.scoring_weights:
                criterion = weight_config.criterion
                score = await self._evaluate_criterion(
                    criterion, 
                    startup_data, 
                    weight_config.custom_factors,
                    market_intelligence
                )
                criterion_scores[criterion.value] = score
            
            # Calculate weighted scores
            weighted_scores = {}
            total_weighted_score = 0.0
            
            for weight_config in investment_thesis.scoring_weights:
                criterion = weight_config.criterion
                raw_score = criterion_scores.get(criterion.value, 0.0)
                weighted_score = raw_score * weight_config.weight
                weighted_scores[criterion.value] = weighted_score
                total_weighted_score += weighted_score
            
            # Calculate overall score (0-100)
            overall_score = total_weighted_score * 100
            
            # Determine recommendation
            recommendation = self._determine_recommendation(
                overall_score, 
                investment_thesis,
                criterion_scores
            )
            
            # Calculate confidence and thesis alignment
            confidence = self._calculate_confidence(criterion_scores, investment_thesis)
            thesis_alignment = self._calculate_thesis_alignment(
                startup_data, 
                investment_thesis
            )
            
            return CustomScore(
                overall_score=overall_score,
                criterion_scores=criterion_scores,
                weighted_scores=weighted_scores,
                recommendation=recommendation,
                confidence=confidence,
                thesis_alignment=thesis_alignment
            )
            
        except Exception as e:
            logger.error(f"Custom scoring calculation failed: {e}")
            return self._create_default_score()
    
    async def _evaluate_criterion(
        self,
        criterion: ScoringCriterion,
        startup_data: Dict[str, Any],
        custom_factors: List[str] = None,
        market_intelligence: Dict[str, Any] = None
    ) -> float:
        """Evaluate a specific scoring criterion"""
        
        try:
            # Prepare evaluation prompt based on criterion
            evaluation_prompt = self._create_criterion_prompt(
                criterion, 
                startup_data, 
                custom_factors,
                market_intelligence
            )
            
            # Get AI evaluation
            response = await self._query_gemini(evaluation_prompt)
            
            # Extract score from response
            import re
            score_match = re.search(r'Score:\s*(\d+(?:\.\d+)?)', response)
            if score_match:
                score = float(score_match.group(1))
                return min(1.0, max(0.0, score / 100))  # Normalize to 0-1
            
            # Fallback scoring based on criterion type
            return self._fallback_criterion_score(criterion, startup_data)
            
        except Exception as e:
            logger.error(f"Criterion evaluation failed for {criterion}: {e}")
            return 0.5  # Default neutral score
    
    def _create_criterion_prompt(
        self,
        criterion: ScoringCriterion,
        startup_data: Dict[str, Any],
        custom_factors: List[str] = None,
        market_intelligence: Dict[str, Any] = None
    ) -> str:
        """Create evaluation prompt for specific criterion"""
        
        base_data = f"Startup Data: {json.dumps(startup_data, indent=2)[:1500]}"
        
        if market_intelligence:
            base_data += f"\nMarket Intelligence: {json.dumps(market_intelligence, indent=2)[:500]}"
        
        criterion_prompts = {
            ScoringCriterion.TEAM_QUALITY: f"""
            Evaluate the team quality for this startup:
            {base_data}
            
            Consider:
            - Founder experience and track record
            - Team composition and skills
            - Previous startup experience
            - Domain expertise
            - Leadership capabilities
            
            Custom factors to consider: {custom_factors or []}
            
            Provide a score from 0-100 and brief explanation.
            Format: Score: XX
            """,
            
            ScoringCriterion.MARKET_SIZE: f"""
            Evaluate the market opportunity for this startup:
            {base_data}
            
            Consider:
            - Total Addressable Market (TAM)
            - Market growth rate
            - Market timing
            - Competitive landscape
            - Market validation
            
            Custom factors to consider: {custom_factors or []}
            
            Provide a score from 0-100 and brief explanation.
            Format: Score: XX
            """,
            
            ScoringCriterion.TRACTION: f"""
            Evaluate the traction and momentum for this startup:
            {base_data}
            
            Consider:
            - Revenue growth
            - User/customer acquisition
            - Product adoption
            - Key partnerships
            - Market validation
            
            Custom factors to consider: {custom_factors or []}
            
            Provide a score from 0-100 and brief explanation.
            Format: Score: XX
            """,
            
            ScoringCriterion.FINANCIAL_HEALTH: f"""
            Evaluate the financial health for this startup:
            {base_data}
            
            Consider:
            - Revenue model sustainability
            - Unit economics (LTV/CAC)
            - Burn rate and runway
            - Profitability path
            - Financial projections realism
            
            Custom factors to consider: {custom_factors or []}
            
            Provide a score from 0-100 and brief explanation.
            Format: Score: XX
            """
        }
        
        return criterion_prompts.get(criterion, f"""
        Evaluate this startup based on {criterion.value}:
        {base_data}
        
        Custom factors to consider: {custom_factors or []}
        
        Provide a score from 0-100 and brief explanation.
        Format: Score: XX
        """)
    
    def _fallback_criterion_score(self, criterion: ScoringCriterion, startup_data: Dict[str, Any]) -> float:
        """Fallback scoring when AI evaluation fails"""
        
        # Simple heuristic-based scoring
        if criterion == ScoringCriterion.FINANCIAL_HEALTH:
            revenue = startup_data.get("financial_data", {}).get("revenue", 0)
            if revenue > 1000000:  # $1M+ revenue
                return 0.8
            elif revenue > 100000:  # $100K+ revenue
                return 0.6
            else:
                return 0.4
        
        elif criterion == ScoringCriterion.TRACTION:
            user_count = startup_data.get("traction_data", {}).get("user_count", 0)
            if user_count > 100000:
                return 0.8
            elif user_count > 10000:
                return 0.6
            else:
                return 0.4
        
        # Default neutral score for other criteria
        return 0.5

    def _determine_recommendation(
        self,
        overall_score: float,
        investment_thesis: InvestmentThesis,
        criterion_scores: Dict[str, float]
    ) -> str:
        """Determine investment recommendation based on score and thesis"""

        # Check minimum threshold
        if overall_score < investment_thesis.minimum_score_threshold:
            return "PASS"

        # Risk-adjusted recommendations
        risk_tolerance = investment_thesis.risk_tolerance

        if overall_score >= 80:
            return "STRONG INVEST"
        elif overall_score >= 70:
            return "INVEST" if risk_tolerance in ["moderate", "aggressive"] else "HOLD"
        elif overall_score >= 60:
            return "HOLD" if risk_tolerance == "aggressive" else "PASS"
        else:
            return "PASS"

    def _calculate_confidence(
        self,
        criterion_scores: Dict[str, float],
        investment_thesis: InvestmentThesis
    ) -> float:
        """Calculate confidence in the scoring"""

        # Higher confidence when:
        # 1. Scores are not all neutral (0.5)
        # 2. Critical criteria have good scores
        # 3. Score distribution is reasonable

        scores = list(criterion_scores.values())
        if not scores:
            return 0.5

        # Check for neutral scores (indicates uncertainty)
        neutral_count = sum(1 for s in scores if abs(s - 0.5) < 0.1)
        neutral_ratio = neutral_count / len(scores)

        # Check critical criteria performance
        critical_weights = [w for w in investment_thesis.scoring_weights if w.importance == "critical"]
        critical_performance = 0.8  # Default if no critical criteria

        if critical_weights:
            critical_scores = [criterion_scores.get(w.criterion.value, 0.5) for w in critical_weights]
            critical_performance = sum(critical_scores) / len(critical_scores)

        # Calculate overall confidence
        confidence = (1 - neutral_ratio) * 0.6 + critical_performance * 0.4
        return min(1.0, max(0.3, confidence))

    def _calculate_thesis_alignment(
        self,
        startup_data: Dict[str, Any],
        investment_thesis: InvestmentThesis
    ) -> float:
        """Calculate how well startup aligns with investment thesis"""

        alignment_score = 0.0
        factors_checked = 0

        # Check sector alignment
        startup_sector = startup_data.get("sector", "").lower()
        if investment_thesis.sector_preferences:
            sector_match = any(
                pref.lower() in startup_sector or startup_sector in pref.lower()
                for pref in investment_thesis.sector_preferences
            )
            alignment_score += 1.0 if sector_match else 0.0
            factors_checked += 1

        # Check stage alignment
        startup_stage = startup_data.get("stage", "").lower()
        if investment_thesis.stage_preferences:
            stage_match = any(
                pref.lower() in startup_stage or startup_stage in pref.lower()
                for pref in investment_thesis.stage_preferences
            )
            alignment_score += 1.0 if stage_match else 0.0
            factors_checked += 1

        # Return normalized alignment score
        return alignment_score / factors_checked if factors_checked > 0 else 0.8

    def _create_default_score(self) -> CustomScore:
        """Create default score when calculation fails"""
        return CustomScore(
            overall_score=50.0,
            criterion_scores={},
            weighted_scores={},
            recommendation="HOLD",
            confidence=0.3,
            thesis_alignment=0.5
        )

    def _create_default_theses(self) -> Dict[str, InvestmentThesis]:
        """Create default investment theses"""

        return {
            "balanced": InvestmentThesis(
                name="Balanced Growth",
                description="Balanced approach focusing on team, market, and traction",
                scoring_weights=[
                    ScoringWeight(ScoringCriterion.TEAM_QUALITY, 0.25, "high"),
                    ScoringWeight(ScoringCriterion.MARKET_SIZE, 0.20, "high"),
                    ScoringWeight(ScoringCriterion.TRACTION, 0.20, "high"),
                    ScoringWeight(ScoringCriterion.BUSINESS_MODEL, 0.15, "medium"),
                    ScoringWeight(ScoringCriterion.FINANCIAL_HEALTH, 0.20, "high")
                ],
                sector_preferences=[],
                stage_preferences=["seed", "series_a"],
                minimum_score_threshold=60.0,
                risk_tolerance="moderate"
            ),

            "tech_focused": InvestmentThesis(
                name="Technology Innovation",
                description="Focus on innovative technology and product differentiation",
                scoring_weights=[
                    ScoringWeight(ScoringCriterion.PRODUCT_INNOVATION, 0.30, "critical"),
                    ScoringWeight(ScoringCriterion.TEAM_QUALITY, 0.25, "high"),
                    ScoringWeight(ScoringCriterion.SCALABILITY, 0.20, "high"),
                    ScoringWeight(ScoringCriterion.COMPETITIVE_ADVANTAGE, 0.15, "medium"),
                    ScoringWeight(ScoringCriterion.MARKET_SIZE, 0.10, "medium")
                ],
                sector_preferences=["AI/ML", "SaaS", "FinTech", "HealthTech"],
                stage_preferences=["seed", "series_a"],
                minimum_score_threshold=70.0,
                risk_tolerance="aggressive"
            ),

            "conservative": InvestmentThesis(
                name="Conservative Growth",
                description="Risk-averse approach focusing on proven metrics",
                scoring_weights=[
                    ScoringWeight(ScoringCriterion.FINANCIAL_HEALTH, 0.30, "critical"),
                    ScoringWeight(ScoringCriterion.TRACTION, 0.25, "critical"),
                    ScoringWeight(ScoringCriterion.BUSINESS_MODEL, 0.20, "high"),
                    ScoringWeight(ScoringCriterion.RISK_PROFILE, 0.15, "high"),
                    ScoringWeight(ScoringCriterion.TEAM_QUALITY, 0.10, "medium")
                ],
                sector_preferences=[],
                stage_preferences=["series_a", "series_b"],
                minimum_score_threshold=75.0,
                risk_tolerance="conservative"
            )
        }

    async def _query_gemini(self, prompt: str) -> str:
        """Query Gemini AI model"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            return "Score: 50"


# Global customizable scoring service instance
customizable_scoring_service = CustomizableScoringService()
