"""
Advanced risk assessment service for startup evaluation
Identifies red flags, inconsistencies, and potential risks using AI
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import re
import asyncio
from datetime import datetime
import numpy as np
import google.generativeai as genai

from app.core.config import settings
from app.models.startup import RiskFlag, RiskLevel
from app.services.benchmarking_service import benchmarking_service

logger = logging.getLogger(__name__)


class RiskAssessmentService:
    """Comprehensive risk assessment for startup evaluation"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Risk detection patterns and thresholds
        self.risk_patterns = {
            "financial_inconsistencies": [
                r"revenue.*(\d+).*million.*(\d+).*thousand",  # Revenue inconsistency
                r"growth.*(\d+)%.*decline",  # Growth contradiction
                r"profitable.*loss.*(\d+)",  # Profitability contradiction
            ],
            "market_size_inflation": [
                r"market.*size.*\$(\d+).*trillion",  # Unrealistic market size
                r"TAM.*\$(\d+).*billion.*niche",  # TAM vs niche contradiction
                r"addressable.*market.*(\d+).*billion.*startup",  # Unrealistic TAM for startup stage
            ],
            "team_red_flags": [
                r"founder.*left.*company",  # Founder departure
                r"co-founder.*conflict",  # Co-founder issues
                r"key.*employee.*turnover",  # High turnover
            ],
            "traction_inconsistencies": [
                r"(\d+).*users.*(\d+).*customers.*ratio",  # User to customer ratio issues
                r"growth.*(\d+)%.*churn.*(\d+)%",  # Growth vs churn inconsistency
                r"viral.*coefficient.*(\d+\.\d+).*low.*growth",  # Viral coefficient vs growth
            ]
        }
        
        # Risk thresholds
        self.risk_thresholds = {
            "revenue_growth_volatility": 0.5,  # High volatility threshold
            "customer_concentration": 0.3,  # >30% revenue from single customer
            "burn_rate_acceleration": 2.0,  # 2x burn rate increase
            "market_size_ratio": 1000,  # Market size to revenue ratio
            "team_turnover_rate": 0.25,  # >25% annual turnover
            "churn_rate_threshold": 0.15,  # >15% monthly churn
        }
    
    async def assess_startup_risks(
        self, 
        startup_data: Dict[str, Any], 
        documents_data: List[Dict[str, Any]]
    ) -> List[RiskFlag]:
        """Comprehensive risk assessment for a startup"""
        
        try:
            risk_flags = []
            
            # 1. Financial Risk Assessment
            financial_risks = await self._assess_financial_risks(startup_data, documents_data)
            risk_flags.extend(financial_risks)
            
            # 2. Market Risk Assessment
            market_risks = await self._assess_market_risks(startup_data, documents_data)
            risk_flags.extend(market_risks)
            
            # 3. Team Risk Assessment
            team_risks = await self._assess_team_risks(startup_data, documents_data)
            risk_flags.extend(team_risks)
            
            # 4. Product/Technology Risk Assessment
            product_risks = await self._assess_product_risks(startup_data, documents_data)
            risk_flags.extend(product_risks)
            
            # 5. Business Model Risk Assessment
            business_risks = await self._assess_business_model_risks(startup_data, documents_data)
            risk_flags.extend(business_risks)
            
            # 6. Data Consistency Risk Assessment
            consistency_risks = await self._assess_data_consistency(startup_data, documents_data)
            risk_flags.extend(consistency_risks)
            
            # 7. AI-Powered Risk Detection
            ai_risks = await self._ai_powered_risk_detection(startup_data, documents_data)
            risk_flags.extend(ai_risks)
            
            # Sort by severity and confidence
            risk_flags.sort(key=lambda x: (x.severity.value, -x.confidence), reverse=True)
            
            return risk_flags
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return []
    
    async def _assess_financial_risks(
        self, 
        startup_data: Dict[str, Any], 
        documents_data: List[Dict[str, Any]]
    ) -> List[RiskFlag]:
        """Assess financial-related risks"""
        
        risks = []
        financial_data = startup_data.get("financial_data", {})
        
        try:
            # Revenue volatility risk
            revenue_history = financial_data.get("revenue_history", [])
            if len(revenue_history) >= 3:
                growth_rates = []
                for i in range(1, len(revenue_history)):
                    if revenue_history[i-1] > 0:
                        growth_rate = (revenue_history[i] - revenue_history[i-1]) / revenue_history[i-1]
                        growth_rates.append(growth_rate)
                
                if growth_rates:
                    volatility = np.std(growth_rates)
                    if volatility > self.risk_thresholds["revenue_growth_volatility"]:
                        risks.append(RiskFlag(
                            flag_type="Financial Risk",
                            severity=RiskLevel.HIGH,
                            description=f"High revenue volatility detected (σ={volatility:.2f}). Inconsistent growth pattern may indicate market or execution issues.",
                            evidence=f"Revenue growth rates: {[f'{r:.1%}' for r in growth_rates]}",
                            confidence=0.85
                        ))
            
            # Burn rate acceleration risk
            burn_rates = financial_data.get("burn_rate_history", [])
            if len(burn_rates) >= 2:
                recent_burn = burn_rates[-1]
                previous_burn = burn_rates[-2]
                if previous_burn > 0:
                    burn_acceleration = recent_burn / previous_burn
                    if burn_acceleration > self.risk_thresholds["burn_rate_acceleration"]:
                        risks.append(RiskFlag(
                            flag_type="Financial Risk",
                            severity=RiskLevel.HIGH,
                            description=f"Burn rate accelerated by {burn_acceleration:.1f}x. May indicate loss of financial discipline or scaling challenges.",
                            evidence=f"Burn rate increased from ${previous_burn:,.0f} to ${recent_burn:,.0f}",
                            confidence=0.90
                        ))
            
            # Customer concentration risk
            customer_concentration = financial_data.get("top_customer_revenue_percentage", 0)
            if customer_concentration > self.risk_thresholds["customer_concentration"]:
                severity = RiskLevel.CRITICAL if customer_concentration > 0.5 else RiskLevel.HIGH
                risks.append(RiskFlag(
                    flag_type="Financial Risk",
                    severity=severity,
                    description=f"High customer concentration risk: {customer_concentration:.1%} of revenue from top customer.",
                    evidence=f"Customer concentration: {customer_concentration:.1%}",
                    confidence=0.95
                ))
            
            # Runway risk
            runway_months = financial_data.get("runway_months", 0)
            if runway_months < 6:
                severity = RiskLevel.CRITICAL if runway_months < 3 else RiskLevel.HIGH
                risks.append(RiskFlag(
                    flag_type="Financial Risk",
                    severity=severity,
                    description=f"Critical runway risk: Only {runway_months} months of runway remaining.",
                    evidence=f"Current runway: {runway_months} months",
                    confidence=0.98
                ))
            
        except Exception as e:
            logger.error(f"Financial risk assessment failed: {e}")
        
        return risks
    
    async def _assess_market_risks(
        self, 
        startup_data: Dict[str, Any], 
        documents_data: List[Dict[str, Any]]
    ) -> List[RiskFlag]:
        """Assess market-related risks"""
        
        risks = []
        market_data = startup_data.get("market_data", {})
        
        try:
            # Market size inflation risk
            tam = market_data.get("tam", 0)
            current_revenue = startup_data.get("financial_data", {}).get("revenue", 0)
            
            if tam > 0 and current_revenue > 0:
                market_ratio = tam / current_revenue
                if market_ratio > self.risk_thresholds["market_size_ratio"]:
                    risks.append(RiskFlag(
                        flag_type="Market Risk",
                        severity=RiskLevel.MEDIUM,
                        description=f"Potentially inflated market size claims. TAM to current revenue ratio: {market_ratio:.0f}x",
                        evidence=f"TAM: ${tam:,.0f}, Current Revenue: ${current_revenue:,.0f}",
                        confidence=0.70
                    ))
            
            # Competition risk
            competitive_threats = market_data.get("competitive_threats", [])
            if len(competitive_threats) > 10:
                risks.append(RiskFlag(
                    flag_type="Market Risk",
                    severity=RiskLevel.MEDIUM,
                    description=f"Highly competitive market with {len(competitive_threats)} identified competitors.",
                    evidence=f"Competitors: {', '.join(competitive_threats[:5])}...",
                    confidence=0.75
                ))
            
            # Market timing risk
            market_maturity = market_data.get("market_maturity", "unknown")
            if market_maturity in ["declining", "saturated"]:
                risks.append(RiskFlag(
                    flag_type="Market Risk",
                    severity=RiskLevel.HIGH,
                    description=f"Market timing risk: Entering a {market_maturity} market.",
                    evidence=f"Market maturity: {market_maturity}",
                    confidence=0.80
                ))
            
        except Exception as e:
            logger.error(f"Market risk assessment failed: {e}")
        
        return risks
    
    async def _assess_team_risks(
        self, 
        startup_data: Dict[str, Any], 
        documents_data: List[Dict[str, Any]]
    ) -> List[RiskFlag]:
        """Assess team-related risks"""
        
        risks = []
        team_data = startup_data.get("team_data", {})
        
        try:
            # Team turnover risk
            turnover_rate = team_data.get("annual_turnover_rate", 0)
            if turnover_rate > self.risk_thresholds["team_turnover_rate"]:
                severity = RiskLevel.HIGH if turnover_rate > 0.4 else RiskLevel.MEDIUM
                risks.append(RiskFlag(
                    flag_type="Team Risk",
                    severity=severity,
                    description=f"High team turnover rate: {turnover_rate:.1%} annually.",
                    evidence=f"Annual turnover rate: {turnover_rate:.1%}",
                    confidence=0.85
                ))
            
            # Founder experience risk
            founder_experience = team_data.get("founder_previous_experience", "")
            if "first-time" in founder_experience.lower() and "technical" not in founder_experience.lower():
                risks.append(RiskFlag(
                    flag_type="Team Risk",
                    severity=RiskLevel.MEDIUM,
                    description="First-time founder without technical background in technical startup.",
                    evidence=f"Founder experience: {founder_experience}",
                    confidence=0.70
                ))
            
            # Key person dependency
            key_person_dependency = team_data.get("key_person_dependency_score", 0)
            if key_person_dependency > 0.8:
                risks.append(RiskFlag(
                    flag_type="Team Risk",
                    severity=RiskLevel.HIGH,
                    description="High dependency on key individuals. Significant risk if key people leave.",
                    evidence=f"Key person dependency score: {key_person_dependency:.2f}",
                    confidence=0.80
                ))
            
        except Exception as e:
            logger.error(f"Team risk assessment failed: {e}")
        
        return risks
    
    async def _assess_product_risks(
        self, 
        startup_data: Dict[str, Any], 
        documents_data: List[Dict[str, Any]]
    ) -> List[RiskFlag]:
        """Assess product and technology risks"""
        
        risks = []
        product_data = startup_data.get("product_data", {})
        
        try:
            # Technical debt risk
            technical_debt_score = product_data.get("technical_debt_score", 0)
            if technical_debt_score > 0.7:
                risks.append(RiskFlag(
                    flag_type="Product Risk",
                    severity=RiskLevel.MEDIUM,
                    description=f"High technical debt may slow development and increase maintenance costs.",
                    evidence=f"Technical debt score: {technical_debt_score:.2f}",
                    confidence=0.75
                ))
            
            # Product-market fit risk
            pmf_indicators = product_data.get("product_market_fit_indicators", {})
            nps_score = pmf_indicators.get("nps_score", 0)
            retention_rate = pmf_indicators.get("retention_rate", 0)
            
            if nps_score < 0 or retention_rate < 0.6:
                risks.append(RiskFlag(
                    flag_type="Product Risk",
                    severity=RiskLevel.HIGH,
                    description="Weak product-market fit indicators suggest market validation issues.",
                    evidence=f"NPS: {nps_score}, Retention: {retention_rate:.1%}",
                    confidence=0.85
                ))
            
            # Scalability risk
            scalability_concerns = product_data.get("scalability_concerns", [])
            if len(scalability_concerns) > 3:
                risks.append(RiskFlag(
                    flag_type="Product Risk",
                    severity=RiskLevel.MEDIUM,
                    description=f"Multiple scalability concerns identified: {len(scalability_concerns)} issues.",
                    evidence=f"Concerns: {', '.join(scalability_concerns[:3])}...",
                    confidence=0.70
                ))
            
        except Exception as e:
            logger.error(f"Product risk assessment failed: {e}")
        
        return risks
    
    async def _assess_business_model_risks(
        self, 
        startup_data: Dict[str, Any], 
        documents_data: List[Dict[str, Any]]
    ) -> List[RiskFlag]:
        """Assess business model risks"""
        
        risks = []
        business_data = startup_data.get("business_model", {})
        
        try:
            # Unit economics risk
            ltv_cac_ratio = business_data.get("ltv_cac_ratio", 0)
            if ltv_cac_ratio < 3.0 and ltv_cac_ratio > 0:
                severity = RiskLevel.HIGH if ltv_cac_ratio < 1.5 else RiskLevel.MEDIUM
                risks.append(RiskFlag(
                    flag_type="Business Model Risk",
                    severity=severity,
                    description=f"Poor unit economics: LTV/CAC ratio of {ltv_cac_ratio:.1f} below healthy threshold of 3.0.",
                    evidence=f"LTV/CAC ratio: {ltv_cac_ratio:.1f}",
                    confidence=0.90
                ))
            
            # Churn rate risk
            churn_rate = business_data.get("monthly_churn_rate", 0)
            if churn_rate > self.risk_thresholds["churn_rate_threshold"]:
                severity = RiskLevel.HIGH if churn_rate > 0.25 else RiskLevel.MEDIUM
                risks.append(RiskFlag(
                    flag_type="Business Model Risk",
                    severity=severity,
                    description=f"High churn rate: {churn_rate:.1%} monthly churn indicates retention issues.",
                    evidence=f"Monthly churn rate: {churn_rate:.1%}",
                    confidence=0.88
                ))
            
            # Revenue model sustainability
            revenue_model = business_data.get("revenue_model", "")
            if "one-time" in revenue_model.lower() and "recurring" not in revenue_model.lower():
                risks.append(RiskFlag(
                    flag_type="Business Model Risk",
                    severity=RiskLevel.MEDIUM,
                    description="One-time revenue model lacks predictability and sustainability.",
                    evidence=f"Revenue model: {revenue_model}",
                    confidence=0.75
                ))
            
        except Exception as e:
            logger.error(f"Business model risk assessment failed: {e}")
        
        return risks
    
    async def _assess_data_consistency(
        self, 
        startup_data: Dict[str, Any], 
        documents_data: List[Dict[str, Any]]
    ) -> List[RiskFlag]:
        """Assess data consistency across documents"""
        
        risks = []
        
        try:
            # Extract metrics from different documents
            metrics_by_document = {}
            
            for doc in documents_data:
                if doc.get("structured_data"):
                    doc_type = doc.get("document_type", "unknown")
                    structured = doc["structured_data"]
                    
                    # Extract common metrics
                    if "revenue" in structured:
                        metrics_by_document.setdefault(doc_type, {})["revenue"] = structured["revenue"]
                    if "user_count" in structured:
                        metrics_by_document.setdefault(doc_type, {})["users"] = structured["user_count"]
                    if "team_size" in structured:
                        metrics_by_document.setdefault(doc_type, {})["team_size"] = structured["team_size"]
            
            # Check for inconsistencies
            if len(metrics_by_document) > 1:
                # Revenue consistency check
                revenues = []
                for doc_type, metrics in metrics_by_document.items():
                    if "revenue" in metrics:
                        revenues.append((doc_type, metrics["revenue"]))
                
                if len(revenues) > 1:
                    revenue_values = [r[1] for r in revenues]
                    if max(revenue_values) / min(revenue_values) > 2.0:  # >2x difference
                        risks.append(RiskFlag(
                            flag_type="Data Consistency Risk",
                            severity=RiskLevel.HIGH,
                            description="Significant revenue inconsistencies across documents.",
                            evidence=f"Revenue values: {', '.join([f'{doc}: ${rev:,.0f}' for doc, rev in revenues])}",
                            confidence=0.85
                        ))
            
        except Exception as e:
            logger.error(f"Data consistency assessment failed: {e}")
        
        return risks
    
    async def _ai_powered_risk_detection(
        self, 
        startup_data: Dict[str, Any], 
        documents_data: List[Dict[str, Any]]
    ) -> List[RiskFlag]:
        """Use AI to detect subtle risks and red flags"""
        
        risks = []
        
        try:
            # Prepare data for AI analysis
            analysis_text = self._prepare_text_for_ai_analysis(startup_data, documents_data)
            
            # AI risk detection prompt
            prompt = f"""
            Analyze the following startup data for potential risks and red flags. Look for:
            1. Inconsistencies in claims or metrics
            2. Unrealistic projections or market size claims
            3. Warning signs in language or tone
            4. Missing critical information
            5. Patterns that suggest potential issues
            
            Data to analyze:
            {analysis_text[:3000]}  # Limit to avoid token limits
            
            Return findings as JSON array with fields:
            - risk_type: Type of risk identified
            - severity: low/medium/high/critical
            - description: Detailed description
            - evidence: Supporting evidence from the data
            - confidence: Confidence score (0-1)
            
            Focus on the most significant risks only.
            """
            
            response = await self._query_gemini(prompt)
            ai_risks_data = self._parse_json_response(response)
            
            # Convert AI findings to RiskFlag objects
            for risk_data in ai_risks_data:
                if isinstance(risk_data, dict):
                    try:
                        risks.append(RiskFlag(
                            flag_type=f"AI-Detected {risk_data.get('risk_type', 'Risk')}",
                            severity=RiskLevel(risk_data.get('severity', 'medium')),
                            description=risk_data.get('description', 'AI-detected risk'),
                            evidence=risk_data.get('evidence', 'AI analysis'),
                            confidence=float(risk_data.get('confidence', 0.7))
                        ))
                    except Exception as e:
                        logger.warning(f"Failed to parse AI risk: {e}")
            
        except Exception as e:
            logger.error(f"AI-powered risk detection failed: {e}")
        
        return risks
    
    def _prepare_text_for_ai_analysis(
        self, 
        startup_data: Dict[str, Any], 
        documents_data: List[Dict[str, Any]]
    ) -> str:
        """Prepare text data for AI analysis"""
        
        text_parts = []
        
        # Add startup data
        if startup_data:
            text_parts.append(f"Startup Data: {str(startup_data)[:1000]}")
        
        # Add document excerpts
        for doc in documents_data[:3]:  # Limit to first 3 documents
            if doc.get("extracted_content", {}).get("raw_text"):
                text_parts.append(f"Document: {doc['extracted_content']['raw_text'][:500]}")
        
        return "\n\n".join(text_parts)
    
    async def _query_gemini(self, prompt: str) -> str:
        """Query Gemini AI model"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            return "[]"
    
    def _parse_json_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse JSON response from AI"""
        try:
            import json
            import re
            
            # Look for JSON array in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return []
        except Exception as e:
            logger.error(f"JSON parsing failed: {e}")
            return []


# Global risk assessment service instance
risk_assessment_service = RiskAssessmentService()
