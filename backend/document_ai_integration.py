"""
Google Document AI Integration for Enhanced Document Processing
Provides advanced document parsing, table extraction, and entity recognition
"""

import os
from typing import Dict, List, Any, Optional
from google.cloud import documentai
import json

class DocumentAIService:
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.location = os.getenv('DOCUMENT_AI_LOCATION', 'us')
        self.processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID')
        
        if self.processor_id:
            self.client = documentai.DocumentProcessorServiceClient()
            self.processor_name = f"projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}"
        else:
            self.client = None
            print("⚠️ Document AI not configured - using fallback processing")
    
    async def process_document(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Process document using Document AI for enhanced extraction
        """
        if not self.client:
            return self._fallback_processing(file_content, mime_type)
        
        try:
            # Configure the process request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=documentai.RawDocument(
                    content=file_content,
                    mime_type=mime_type
                )
            )
            
            # Process the document
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract structured data
            extracted_data = {
                'text': document.text,
                'entities': self._extract_entities(document),
                'tables': self._extract_tables(document),
                'key_value_pairs': self._extract_key_value_pairs(document),
                'financial_data': self._extract_financial_data(document),
                'confidence_score': self._calculate_confidence(document)
            }
            
            print(f"✅ Document AI processing completed with {len(extracted_data['entities'])} entities")
            return extracted_data
            
        except Exception as e:
            print(f"❌ Document AI processing failed: {e}")
            return self._fallback_processing(file_content, mime_type)
    
    def _extract_entities(self, document) -> List[Dict[str, Any]]:
        """Extract named entities from document"""
        entities = []
        
        for entity in document.entities:
            entities.append({
                'type': entity.type_,
                'text': entity.text_anchor.content if entity.text_anchor else '',
                'confidence': entity.confidence,
                'normalized_value': entity.normalized_value.text if entity.normalized_value else None
            })
        
        return entities
    
    def _extract_tables(self, document) -> List[Dict[str, Any]]:
        """Extract tables from document"""
        tables = []
        
        for page in document.pages:
            for table in page.tables:
                table_data = {
                    'headers': [],
                    'rows': [],
                    'confidence': 0.0
                }
                
                # Extract table structure
                for row_idx, row in enumerate(table.header_rows):
                    header_row = []
                    for cell in row.cells:
                        cell_text = self._get_cell_text(cell, document.text)
                        header_row.append(cell_text)
                    table_data['headers'].append(header_row)
                
                for row in table.body_rows:
                    body_row = []
                    for cell in row.cells:
                        cell_text = self._get_cell_text(cell, document.text)
                        body_row.append(cell_text)
                    table_data['rows'].append(body_row)
                
                tables.append(table_data)
        
        return tables
    
    def _extract_key_value_pairs(self, document) -> Dict[str, str]:
        """Extract key-value pairs from document"""
        kv_pairs = {}
        
        for page in document.pages:
            for form_field in page.form_fields:
                key = self._get_field_name(form_field.field_name, document.text)
                value = self._get_field_value(form_field.field_value, document.text)
                
                if key and value:
                    kv_pairs[key] = value
        
        return kv_pairs
    
    def _extract_financial_data(self, document) -> Dict[str, Any]:
        """Extract financial metrics from document"""
        financial_data = {
            'revenue_figures': [],
            'growth_rates': [],
            'funding_amounts': [],
            'valuation': None,
            'burn_rate': None
        }
        
        # Look for financial patterns in entities
        for entity in document.entities:
            entity_type = entity.type_.lower()
            entity_text = entity.text_anchor.content if entity.text_anchor else ''
            
            if 'money' in entity_type or 'currency' in entity_type:
                if 'revenue' in entity_text.lower():
                    financial_data['revenue_figures'].append(entity_text)
                elif 'funding' in entity_text.lower() or 'raised' in entity_text.lower():
                    financial_data['funding_amounts'].append(entity_text)
                elif 'valuation' in entity_text.lower():
                    financial_data['valuation'] = entity_text
            
            elif 'percent' in entity_type:
                if 'growth' in entity_text.lower():
                    financial_data['growth_rates'].append(entity_text)
        
        return financial_data
    
    def _get_cell_text(self, cell, document_text: str) -> str:
        """Extract text from table cell"""
        if not cell.layout.text_anchor:
            return ""
        
        start_index = cell.layout.text_anchor.text_segments[0].start_index
        end_index = cell.layout.text_anchor.text_segments[0].end_index
        
        return document_text[start_index:end_index].strip()
    
    def _get_field_name(self, field_name, document_text: str) -> str:
        """Extract field name text"""
        if not field_name or not field_name.text_anchor:
            return ""
        
        start_index = field_name.text_anchor.text_segments[0].start_index
        end_index = field_name.text_anchor.text_segments[0].end_index
        
        return document_text[start_index:end_index].strip()
    
    def _get_field_value(self, field_value, document_text: str) -> str:
        """Extract field value text"""
        if not field_value or not field_value.text_anchor:
            return ""
        
        start_index = field_value.text_anchor.text_segments[0].start_index
        end_index = field_value.text_anchor.text_segments[0].end_index
        
        return document_text[start_index:end_index].strip()
    
    def _calculate_confidence(self, document) -> float:
        """Calculate overall confidence score"""
        if not document.entities:
            return 0.5
        
        total_confidence = sum(entity.confidence for entity in document.entities)
        return total_confidence / len(document.entities)
    
    def _fallback_processing(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """Fallback processing when Document AI is not available"""
        return {
            'text': '',  # Would use PyPDF2 or python-docx
            'entities': [],
            'tables': [],
            'key_value_pairs': {},
            'financial_data': {
                'revenue_figures': [],
                'growth_rates': [],
                'funding_amounts': [],
                'valuation': None,
                'burn_rate': None
            },
            'confidence_score': 0.3,
            'processing_method': 'fallback'
        }

# Global instance
document_ai_service = DocumentAIService()

async def enhance_document_processing(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Enhanced document processing using Document AI
    """
    try:
        # Determine MIME type
        mime_type = 'application/pdf' if filename.lower().endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        # Process with Document AI
        processed_data = await document_ai_service.process_document(file_content, mime_type)
        
        # Enhance with additional analysis
        enhanced_data = {
            **processed_data,
            'filename': filename,
            'processing_timestamp': '2025-09-19T10:00:00Z',
            'enhanced_metrics': {
                'entity_count': len(processed_data.get('entities', [])),
                'table_count': len(processed_data.get('tables', [])),
                'financial_data_found': bool(processed_data.get('financial_data', {}).get('revenue_figures')),
                'confidence_level': 'high' if processed_data.get('confidence_score', 0) > 0.8 else 'medium'
            }
        }
        
        return enhanced_data
        
    except Exception as e:
        print(f"❌ Enhanced document processing failed: {e}")
        return {
            'text': '',
            'entities': [],
            'tables': [],
            'key_value_pairs': {},
            'financial_data': {},
            'confidence_score': 0.0,
            'error': str(e)
        }
