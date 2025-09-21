"""
Multi-Source Data Ingestion Pipeline
Processes call transcripts, emails, founder updates, and other communication data
"""

import logging
import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import google.generativeai as genai
from google.cloud import speech
from google.cloud import translate_v2 as translate

from app.core.config import settings
from app.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

@dataclass
class ProcessedCommunication:
    """Processed communication data structure"""
    source_type: str  # call_transcript, email, founder_update, etc.
    content: str
    metadata: Dict[str, Any]
    extracted_insights: Dict[str, Any]
    sentiment_score: float
    key_topics: List[str]
    risk_indicators: List[str]
    timestamp: datetime

class MultiSourceIngestionService:
    """Service for ingesting and processing multiple data sources"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.document_processor = DocumentProcessor()
        
        # Initialize Google Cloud services
        try:
            self.speech_client = speech.SpeechClient()
            self.translate_client = translate.Client()
        except Exception as e:
            logger.warning(f"Google Cloud services not available: {e}")
            self.speech_client = None
            self.translate_client = None
    
    async def process_call_transcript(
        self, 
        audio_file_path: Optional[str] = None,
        transcript_text: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> ProcessedCommunication:
        """Process call transcript from audio or text"""
        
        try:
            # Convert audio to text if needed
            if audio_file_path and not transcript_text:
                transcript_text = await self._transcribe_audio(audio_file_path)
            
            if not transcript_text:
                raise ValueError("No transcript text available")
            
            # Extract insights from transcript
            insights = await self._extract_call_insights(transcript_text)
            
            # Analyze sentiment
            sentiment_score = await self._analyze_sentiment(transcript_text)
            
            # Extract key topics
            key_topics = await self._extract_key_topics(transcript_text)
            
            # Identify risk indicators
            risk_indicators = await self._identify_risk_indicators(transcript_text)
            
            return ProcessedCommunication(
                source_type="call_transcript",
                content=transcript_text,
                metadata=metadata or {},
                extracted_insights=insights,
                sentiment_score=sentiment_score,
                key_topics=key_topics,
                risk_indicators=risk_indicators,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Call transcript processing failed: {e}")
            raise
    
    async def process_email_thread(
        self, 
        emails: List[Dict[str, Any]]
    ) -> ProcessedCommunication:
        """Process email thread between founders and investors"""
        
        try:
            # Combine email thread into coherent narrative
            combined_content = self._combine_email_thread(emails)
            
            # Extract business insights from emails
            insights = await self._extract_email_insights(combined_content, emails)
            
            # Analyze communication sentiment
            sentiment_score = await self._analyze_sentiment(combined_content)
            
            # Extract key topics and concerns
            key_topics = await self._extract_key_topics(combined_content)
            
            # Identify risk indicators in communication
            risk_indicators = await self._identify_risk_indicators(combined_content)
            
            return ProcessedCommunication(
                source_type="email_thread",
                content=combined_content,
                metadata={"email_count": len(emails), "participants": self._extract_participants(emails)},
                extracted_insights=insights,
                sentiment_score=sentiment_score,
                key_topics=key_topics,
                risk_indicators=risk_indicators,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Email thread processing failed: {e}")
            raise
    
    async def process_founder_update(
        self, 
        update_content: str,
        update_type: str = "monthly_update",
        metadata: Dict[str, Any] = None
    ) -> ProcessedCommunication:
        """Process founder updates and investor communications"""
        
        try:
            # Extract business metrics and updates
            insights = await self._extract_update_insights(update_content, update_type)
            
            # Analyze sentiment and tone
            sentiment_score = await self._analyze_sentiment(update_content)
            
            # Extract key topics and milestones
            key_topics = await self._extract_key_topics(update_content)
            
            # Identify potential concerns or red flags
            risk_indicators = await self._identify_risk_indicators(update_content)
            
            return ProcessedCommunication(
                source_type="founder_update",
                content=update_content,
                metadata=metadata or {"update_type": update_type},
                extracted_insights=insights,
                sentiment_score=sentiment_score,
                key_topics=key_topics,
                risk_indicators=risk_indicators,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Founder update processing failed: {e}")
            raise
    
    async def process_mixed_documents(
        self, 
        documents: List[Dict[str, Any]]
    ) -> List[ProcessedCommunication]:
        """Process multiple document types in batch"""
        
        processed_communications = []
        
        for doc in documents:
            try:
                doc_type = doc.get("type", "unknown")
                
                if doc_type == "call_transcript":
                    result = await self.process_call_transcript(
                        transcript_text=doc.get("content"),
                        metadata=doc.get("metadata", {})
                    )
                elif doc_type == "email_thread":
                    result = await self.process_email_thread(doc.get("emails", []))
                elif doc_type == "founder_update":
                    result = await self.process_founder_update(
                        update_content=doc.get("content"),
                        update_type=doc.get("update_type", "general"),
                        metadata=doc.get("metadata", {})
                    )
                else:
                    # Process as general document
                    result = await self._process_general_document(doc)
                
                processed_communications.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process document {doc.get('id', 'unknown')}: {e}")
                continue
        
        return processed_communications
    
    async def _transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file to text using Google Speech-to-Text"""
        
        if not self.speech_client:
            raise ValueError("Speech client not available")
        
        try:
            # Read audio file
            with open(audio_file_path, 'rb') as audio_file:
                content = audio_file.read()
            
            # Configure recognition
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="en-US",
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True,
            )
            
            # Perform transcription
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Combine results
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
            
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise
    
    async def _extract_call_insights(self, transcript: str) -> Dict[str, Any]:
        """Extract business insights from call transcript"""
        
        prompt = f"""
        Analyze this investor call transcript and extract key business insights:
        
        Transcript: {transcript[:2000]}
        
        Extract and return as JSON:
        {{
            "key_metrics_discussed": [],
            "business_updates": [],
            "challenges_mentioned": [],
            "future_plans": [],
            "investor_concerns": [],
            "founder_confidence_level": "high/medium/low",
            "next_steps": [],
            "funding_discussions": {{
                "amount_discussed": null,
                "timeline": null,
                "use_of_funds": []
            }}
        }}
        """
        
        try:
            response = await self._query_gemini(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Call insight extraction failed: {e}")
            return {}
    
    async def _extract_email_insights(self, content: str, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract insights from email communications"""
        
        prompt = f"""
        Analyze this email thread between founders and investors:
        
        Content: {content[:2000]}
        
        Extract and return as JSON:
        {{
            "communication_frequency": "high/medium/low",
            "response_times": [],
            "key_topics_discussed": [],
            "concerns_raised": [],
            "commitments_made": [],
            "follow_up_actions": [],
            "relationship_health": "strong/good/concerning",
            "transparency_level": "high/medium/low"
        }}
        """
        
        try:
            response = await self._query_gemini(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Email insight extraction failed: {e}")
            return {}

    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text content"""

        prompt = f"""
        Analyze the sentiment of this text and return a score from -1.0 (very negative) to 1.0 (very positive):

        Text: {text[:1000]}

        Return only a decimal number between -1.0 and 1.0.
        """

        try:
            response = await self._query_gemini(prompt)
            # Extract number from response
            import re
            number_match = re.search(r'-?\d+\.?\d*', response)
            if number_match:
                score = float(number_match.group())
                return max(-1.0, min(1.0, score))  # Clamp to [-1, 1]
            return 0.0
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return 0.0

    async def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from text"""

        prompt = f"""
        Extract the top 5-10 key topics from this text:

        Text: {text[:1500]}

        Return as JSON array of strings: ["topic1", "topic2", ...]
        """

        try:
            response = await self._query_gemini(prompt)
            topics = self._parse_json_response(response)
            return topics if isinstance(topics, list) else []
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return []

    async def _identify_risk_indicators(self, text: str) -> List[str]:
        """Identify potential risk indicators in text"""

        prompt = f"""
        Identify potential risk indicators or red flags in this text:

        Text: {text[:1500]}

        Look for:
        - Financial concerns
        - Team issues
        - Market challenges
        - Product problems
        - Competitive threats
        - Regulatory issues

        Return as JSON array of strings: ["risk1", "risk2", ...]
        """

        try:
            response = await self._query_gemini(prompt)
            risks = self._parse_json_response(response)
            return risks if isinstance(risks, list) else []
        except Exception as e:
            logger.error(f"Risk indicator identification failed: {e}")
            return []

    def _combine_email_thread(self, emails: List[Dict[str, Any]]) -> str:
        """Combine email thread into coherent text"""

        combined = []
        for email in emails:
            sender = email.get("sender", "Unknown")
            subject = email.get("subject", "")
            body = email.get("body", "")
            timestamp = email.get("timestamp", "")

            combined.append(f"From: {sender} | Subject: {subject} | Time: {timestamp}")
            combined.append(body)
            combined.append("---")

        return "\n".join(combined)

    def _extract_participants(self, emails: List[Dict[str, Any]]) -> List[str]:
        """Extract unique participants from email thread"""

        participants = set()
        for email in emails:
            if email.get("sender"):
                participants.add(email["sender"])
            if email.get("recipients"):
                participants.update(email["recipients"])

        return list(participants)

    async def _process_general_document(self, doc: Dict[str, Any]) -> ProcessedCommunication:
        """Process general document type"""

        content = doc.get("content", "")

        # Extract insights
        insights = await self._extract_general_insights(content)

        # Analyze sentiment
        sentiment_score = await self._analyze_sentiment(content)

        # Extract topics
        key_topics = await self._extract_key_topics(content)

        # Identify risks
        risk_indicators = await self._identify_risk_indicators(content)

        return ProcessedCommunication(
            source_type=doc.get("type", "general_document"),
            content=content,
            metadata=doc.get("metadata", {}),
            extracted_insights=insights,
            sentiment_score=sentiment_score,
            key_topics=key_topics,
            risk_indicators=risk_indicators,
            timestamp=datetime.utcnow()
        )

    async def _extract_general_insights(self, content: str) -> Dict[str, Any]:
        """Extract general business insights from document"""

        prompt = f"""
        Extract key business insights from this document:

        Content: {content[:2000]}

        Return as JSON:
        {{
            "business_model": "",
            "key_metrics": {{}},
            "market_position": "",
            "competitive_advantages": [],
            "challenges": [],
            "opportunities": [],
            "financial_highlights": {{}},
            "team_strengths": []
        }}
        """

        try:
            response = await self._query_gemini(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"General insight extraction failed: {e}")
            return {}

    async def _query_gemini(self, prompt: str) -> str:
        """Query Gemini AI model"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            return ""

    def _parse_json_response(self, response: str) -> Union[Dict[str, Any], List[Any]]:
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


# Global multi-source ingestion service instance
multi_source_service = MultiSourceIngestionService()
    
    async def _extract_update_insights(self, content: str, update_type: str) -> Dict[str, Any]:
        """Extract insights from founder updates"""
        
        prompt = f"""
        Analyze this founder update ({update_type}):
        
        Content: {content[:2000]}
        
        Extract and return as JSON:
        {{
            "metrics_reported": {{}},
            "milestones_achieved": [],
            "challenges_faced": [],
            "team_updates": [],
            "product_progress": [],
            "market_feedback": [],
            "financial_status": {{}},
            "next_month_goals": [],
            "help_needed": [],
            "overall_momentum": "accelerating/steady/slowing"
        }}
        """
        
        try:
            response = await self._query_gemini(prompt)
            return self._parse_json_response(response)
        except Exception as e:
            logger.error(f"Update insight extraction failed: {e}")
            return {}
