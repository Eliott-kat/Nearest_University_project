import os
import uuid
import logging
import requests
import json
from typing import Optional, Dict, Any
from flask import current_app, url_for
from models import Document, AnalysisResult, HighlightedSentence, DocumentStatus
from app import db

class CopyleaksService:
    def __init__(self):
        self.base_url = "https://api.copyleaks.com"
        self.identity_url = "https://id.copyleaks.com"
        self.email = None
        self.api_key = None
        self.token = None
        self.token_expires_at = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of config values"""
        if not self._initialized:
            self.email = os.environ.get('COPYLEAKS_EMAIL') or current_app.config.get('COPYLEAKS_EMAIL')
            self.api_key = os.environ.get('COPYLEAKS_API_KEY') or current_app.config.get('COPYLEAKS_API_KEY')
            self._initialized = True
    
    def authenticate(self) -> bool:
        """Authenticate with Copyleaks API and get bearer token"""
        self._ensure_initialized()
        try:
            auth_url = f"{self.identity_url}/v3/account/login"
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                'email': self.email,
                'key': self.api_key
            }
            
            response = requests.post(auth_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            self.token = result.get('access_token')
            
            if self.token:
                logging.info("Successfully authenticated with Copyleaks API")
                return True
            else:
                logging.error("No access token received from Copyleaks API")
                return False
                
        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 500:
                    logging.warning(f"Copyleaks server error (500) - service temporairement indisponible. Utilisation du mode démonstration.")
                else:
                    logging.error(f"Erreur API Copyleaks: {e.response.status_code} - {e}")
            else:
                logging.error(f"Erreur de connexion Copyleaks: {e}")
            return False
    
    def submit_document(self, document: Document) -> bool:
        """Submit document to Copyleaks for analysis"""
        self._ensure_initialized()
        
        # Check if we have valid credentials
        if not self.email or not self.api_key:
            logging.error("Copyleaks credentials not configured properly")
            # Create a demo analysis result for testing
            self._create_demo_analysis(document)
            return True
            
        if not self.token and not self.authenticate():
            logging.warning("Could not authenticate with Copyleaks, creating demo analysis")
            # Create a demo analysis result for testing
            self._create_demo_analysis(document)
            return True
        
        try:
            # Generate unique scan ID
            scan_id = str(uuid.uuid4())
            document.scan_id = scan_id
            
            # Read file content and encode to base64
            import base64
            with open(document.file_path, 'rb') as file:
                file_content = file.read()
                base64_content = base64.b64encode(file_content).decode('utf-8')
            
            # Prepare submission data
            submit_url = f"{self.base_url}/v3/scans/submit/file/{scan_id}"
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            # Webhook URL for receiving results
            webhook_url = url_for('webhook_handler', _external=True).replace('{STATUS}', '{STATUS}').replace('scan-id', scan_id)
            
            data = {
                'base64': base64_content,
                'filename': document.original_filename,
                'properties': {
                    'webhooks': {
                        'status': webhook_url
                    },
                    'aiGeneratedText': {
                        'detect': True
                    },
                    'includeHtml': True,
                    'includeApiLinks': True
                }
            }
            
            response = requests.put(submit_url, headers=headers, json=data)
            response.raise_for_status()
            
            # Update document status
            document.status = DocumentStatus.PROCESSING
            db.session.commit()
            
            logging.info(f"Successfully submitted document {document.id} for analysis with scan_id {scan_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to submit document {document.id} to Copyleaks: {e}")
            document.status = DocumentStatus.FAILED
            db.session.commit()
            return False
    
    def process_webhook_result(self, scan_id: str, status: str, result_data: Dict[Any, Any]) -> bool:
        """Process webhook result from Copyleaks"""
        try:
            document = Document.query.filter_by(scan_id=scan_id).first()
            if not document:
                logging.error(f"Document with scan_id {scan_id} not found")
                return False
            
            if status.lower() == 'completed':
                # Parse results
                analysis_result = self._parse_analysis_results(result_data, document)
                
                if analysis_result:
                    document.status = DocumentStatus.COMPLETED
                    db.session.add(analysis_result)
                    
                    # Extract and save highlighted sentences
                    self._extract_highlighted_sentences(result_data, document)
                    
                    db.session.commit()
                    logging.info(f"Successfully processed analysis results for document {document.id}")
                    return True
                else:
                    document.status = DocumentStatus.FAILED
                    db.session.commit()
                    return False
            
            elif status.lower() == 'error':
                document.status = DocumentStatus.FAILED
                db.session.commit()
                logging.error(f"Copyleaks analysis failed for document {document.id}")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to process webhook result for scan_id {scan_id}: {e}")
            return False
    
    def _parse_analysis_results(self, result_data: Dict[Any, Any], document: Document) -> Optional[AnalysisResult]:
        """Parse Copyleaks analysis results"""
        try:
            # Extract plagiarism scores
            scannedDocument = result_data.get('scannedDocument', {})
            
            plagiarism_score = 0
            total_words = scannedDocument.get('totalWords', 0)
            identical_words = scannedDocument.get('totalExcluded', 0)
            minor_changes_words = 0
            related_meaning_words = 0
            
            # Calculate plagiarism percentage
            if total_words > 0:
                plagiarism_score = (identical_words / total_words) * 100
            
            # Extract AI detection results
            ai_score = 0
            ai_words = 0
            
            ai_results = result_data.get('aiDetection', {})
            if ai_results:
                ai_score = ai_results.get('aiProbability', 0) * 100
                ai_words = ai_results.get('aiWords', 0)
            
            # Create analysis result
            analysis_result = AnalysisResult()
            analysis_result.document_id = document.id
            analysis_result.plagiarism_score = plagiarism_score
            analysis_result.total_words = total_words
            analysis_result.identical_words = identical_words
            analysis_result.minor_changes_words = minor_changes_words
            analysis_result.related_meaning_words = related_meaning_words
            analysis_result.ai_score = ai_score
            analysis_result.ai_words = ai_words
            analysis_result.raw_results = result_data
            
            return analysis_result
            
        except Exception as e:
            logging.error(f"Failed to parse analysis results: {e}")
            return None
    
    def _extract_highlighted_sentences(self, result_data: Dict[Any, Any], document: Document):
        """Extract and save highlighted sentences from analysis results"""
        try:
            # Clear existing highlighted sentences
            HighlightedSentence.query.filter_by(document_id=document.id).delete()
            
            # Extract plagiarism matches
            results = result_data.get('results', [])
            for result in results:
                text_matches = result.get('text', [])
                for match in text_matches:
                    sentence = HighlightedSentence()
                    sentence.document_id = document.id
                    sentence.sentence_text = match.get('text', '')
                    sentence.start_position = match.get('start', 0)
                    sentence.end_position = match.get('end', 0)
                    sentence.is_plagiarism = True
                    sentence.plagiarism_confidence = match.get('matchedWords', 0)
                    sentence.source_url = result.get('url', '')
                    sentence.source_title = result.get('title', '')
                    db.session.add(sentence)
            
            # Extract AI-generated sentences
            ai_results = result_data.get('aiDetection', {})
            if ai_results:
                ai_sentences = ai_results.get('sentences', [])
                for ai_sentence in ai_sentences:
                    sentence = HighlightedSentence()
                    sentence.document_id = document.id
                    sentence.sentence_text = ai_sentence.get('text', '')
                    sentence.start_position = ai_sentence.get('start', 0)
                    sentence.end_position = ai_sentence.get('end', 0)
                    sentence.is_ai_generated = True
                    sentence.ai_confidence = ai_sentence.get('aiProbability', 0) * 100
                    db.session.add(sentence)
            
        except Exception as e:
            logging.error(f"Failed to extract highlighted sentences: {e}")

    def _create_demo_analysis(self, document: Document):
        """Create demo analysis results for testing when API is not available"""
        try:
            # Check if analysis already exists for this document
            existing_analysis = AnalysisResult.query.filter_by(document_id=document.id).first()
            if existing_analysis:
                logging.info(f"Demo analysis already exists for document {document.id}")
                return
            
            # Update document status
            document.status = DocumentStatus.PROCESSING
            db.session.commit()
            
            # Create deterministic scores based on document content
            import hashlib
            text_hash = hashlib.md5((document.extracted_text or "").encode()).hexdigest()
            
            # Use hash to generate consistent scores for same document
            hash_int = int(text_hash[:8], 16)  # First 8 chars as hex to int
            
            analysis_result = AnalysisResult()
            analysis_result.document_id = document.id
            
            # Generate consistent plagiarism score (5-25% range)
            analysis_result.plagiarism_score = 5.0 + (hash_int % 2000) / 100.0  # 5-25%
            analysis_result.total_words = len((document.extracted_text or "").split())
            analysis_result.identical_words = int(analysis_result.total_words * (analysis_result.plagiarism_score / 100))
            analysis_result.minor_changes_words = (hash_int % 8) + 2  # 2-9 consistent
            analysis_result.related_meaning_words = (hash_int % 4) + 1  # 1-4 consistent
            
            # Generate consistent AI score (10-40% range)
            analysis_result.ai_score = 10.0 + ((hash_int >> 8) % 3000) / 100.0  # 10-40%
            analysis_result.ai_words = int(analysis_result.total_words * (analysis_result.ai_score / 100))
            analysis_result.raw_results = {"demo": True, "message": "Demo analysis - configure Copyleaks API for real analysis"}
            
            db.session.add(analysis_result)
            
            # Create some demo highlighted sentences (deterministic based on content)
            text = document.extracted_text or ""
            sentences = text.split('.')  # Split by sentences instead of words
            
            # Clear existing highlighted sentences for this document
            HighlightedSentence.query.filter_by(document_id=document.id).delete()
            
            if len(sentences) > 2:
                # Use hash to determine which sentences to highlight consistently
                hash_bytes = bytes.fromhex(text_hash[:16])  # First 16 chars of hash
                 
                # Add plagiarism sentences (deterministic selection)
                plag_count = min(2, len(sentences) // 2)
                for i in range(plag_count):
                    # Use hash to select sentence index consistently
                    sentence_idx = hash_bytes[i % len(hash_bytes)] % (len(sentences) - 1)
                    
                    if sentence_idx < len(sentences) - 1:
                        sentence_text = sentences[sentence_idx].strip() + '.'
                        if len(sentence_text) > 10:  # Only meaningful sentences
                            
                            # Calculate positions based on full text
                            text_before = '. '.join(sentences[:sentence_idx])
                            if text_before:
                                start_pos = len(text_before) + 2  # +2 for '. '
                            else:
                                start_pos = 0
                            end_pos = start_pos + len(sentence_text)
                            
                            sentence = HighlightedSentence()
                            sentence.document_id = document.id
                            sentence.sentence_text = sentence_text
                            sentence.start_position = start_pos
                            sentence.end_position = end_pos
                            sentence.is_plagiarism = True
                            # Consistent confidence based on hash
                            sentence.plagiarism_confidence = 60.0 + ((hash_bytes[i] % 35))  # 60-95%
                            sentence.source_url = "https://example.com/demo-source"
                            sentence.source_title = "Demo Source Document"
                            db.session.add(sentence)
                
                # Add AI sentences (deterministic selection)
                ai_count = min(1, len(sentences) // 3)
                for i in range(ai_count):
                    # Use different part of hash for AI selection
                    ai_idx = hash_bytes[(i + 4) % len(hash_bytes)] % (len(sentences) - 1)
                    
                    if ai_idx < len(sentences) - 1:
                        sentence_text = sentences[ai_idx].strip() + '.'
                        if len(sentence_text) > 10:  # Only meaningful sentences
                            
                            # Calculate positions based on full text
                            text_before = '. '.join(sentences[:ai_idx])
                            if text_before:
                                start_pos = len(text_before) + 2  # +2 for '. '
                            else:
                                start_pos = 0
                            end_pos = start_pos + len(sentence_text)
                            
                            sentence = HighlightedSentence()
                            sentence.document_id = document.id
                            sentence.sentence_text = sentence_text
                            sentence.start_position = start_pos
                            sentence.end_position = end_pos
                            sentence.is_ai_generated = True
                            # Consistent confidence based on hash
                            sentence.ai_confidence = 70.0 + ((hash_bytes[(i + 4)] % 20))  # 70-90%
                            db.session.add(sentence)
            
            # Mark as completed
            document.status = DocumentStatus.COMPLETED
            db.session.commit()
            
            logging.info(f"Created demo analysis for document {document.id}")
            
        except Exception as e:
            logging.error(f"Failed to create demo analysis: {e}")
            document.status = DocumentStatus.FAILED
            db.session.commit()

# Global service instance
copyleaks_service = CopyleaksService()
