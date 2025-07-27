"""
Service hybride d'analyse : GPTZero API pour l'IA + Traitement local pour le plagiat
Architecture conforme aux spécifications demandées
"""

import logging
from typing import Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from gptzero_service_class import GPTZeroService
from local_plagiarism_service import local_plagiarism_service
from models import Document, AnalysisResult, HighlightedSentence, db
from datetime import datetime

class HybridAnalysisService:
    """
    Service hybride combinant :
    - GPTZero API (cloud) pour la détection IA
    - Traitement local (TF-IDF + SentenceTransformer) pour le plagiat
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Services spécialisés
        self.gptzero_service = GPTZeroService()
        self.local_plagiarism = local_plagiarism_service
        
        # Configuration
        self.max_workers = 2  # Parallélisation des analyses
        
        self.logger.info("Service d'analyse hybride initialisé")
    
    def analyze_document(self, document: Document, text: str) -> Dict[str, Any]:
        """
        Analyser un document avec l'approche hybride :
        1. Détection IA via GPTZero API (cloud)
        2. Détection plagiat via traitement local
        """
        try:
            self.logger.info(f"Début analyse hybride pour document {document.id}")
            
            # Validation des entrées
            if not text or len(text.strip()) < 50:
                return self._create_error_result("Texte trop court pour l'analyse")
            
            # Ajouter le document à la base locale pour futures comparaisons
            if document.file_path:
                self.local_plagiarism.add_document_to_database(document.file_path, document.id)
            
            # Exécuter les analyses en parallèle
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Lancer l'analyse IA (GPTZero)
                ai_future = executor.submit(self._analyze_ai_content, text)
                
                # Lancer l'analyse plagiat (local)
                plagiarism_future = executor.submit(self._analyze_plagiarism_content, text)
                
                # Récupérer les résultats
                ai_result = ai_future.result()
                plagiarism_result = plagiarism_future.result()
            
            # Combiner les résultats
            combined_result = self._combine_results(ai_result, plagiarism_result, document)
            
            # Sauvegarder en base de données
            self._save_analysis_results(document, combined_result, text)
            
            self.logger.info(f"Analyse hybride terminée pour document {document.id}")
            return combined_result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse hybride : {e}")
            return self._create_error_result(f"Erreur d'analyse : {str(e)}")
    
    def _analyze_ai_content(self, text: str) -> Dict[str, Any]:
        """Analyser le contenu IA via GPTZero API"""
        try:
            self.logger.info("Analyse IA via GPTZero API...")
            
            # Utiliser le service GPTZero existant
            result = self.gptzero_service.analyze_text(text)
            
            if result.get('success'):
                return {
                    'success': True,
                    'ai_score': result.get('ai_probability', 0),
                    'method': 'gptzero_api',
                    'details': result.get('details', {}),
                    'sentences': result.get('sentences', [])
                }
            else:
                return {
                    'success': False,
                    'ai_score': 0,
                    'method': 'gptzero_api',
                    'error': result.get('error', 'Erreur API GPTZero')
                }
                
        except Exception as e:
            self.logger.error(f"Erreur analyse IA : {e}")
            return {
                'success': False,
                'ai_score': 0,
                'method': 'gptzero_api',
                'error': str(e)
            }
    
    def _analyze_plagiarism_content(self, text: str) -> Dict[str, Any]:
        """Analyser le plagiat via traitement local"""
        try:
            self.logger.info("Analyse plagiat via traitement local...")
            
            # Utiliser le service local de plagiat
            result = self.local_plagiarism.analyze_plagiarism(text)
            
            return {
                'success': True,
                'plagiarism_score': result.get('plagiarism_score', 0),
                'method': 'local_hybrid',
                'matches': result.get('matches', []),
                'details': result.get('detection_details', {}),
                'total_compared': result.get('total_documents_compared', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur analyse plagiat : {e}")
            return {
                'success': False,
                'plagiarism_score': 0,
                'method': 'local_hybrid',
                'error': str(e)
            }
    
    def _combine_results(self, ai_result: Dict, plagiarism_result: Dict, document: Document) -> Dict[str, Any]:
        """Combiner les résultats des deux analyses"""
        
        # Scores principaux
        ai_score = ai_result.get('ai_score', 0)
        plagiarism_score = plagiarism_result.get('plagiarism_score', 0)
        
        # Statut global
        success = ai_result.get('success', False) or plagiarism_result.get('success', False)
        
        # Messages d'erreur
        errors = []
        if not ai_result.get('success'):
            errors.append(f"IA: {ai_result.get('error', 'Erreur inconnue')}")
        if not plagiarism_result.get('success'):
            errors.append(f"Plagiat: {plagiarism_result.get('error', 'Erreur inconnue')}")
        
        # Évaluation du risque global
        risk_level = self._calculate_risk_level(ai_score, plagiarism_score)
        
        return {
            'success': success,
            'analysis_method': 'hybrid_gptzero_local',
            'timestamp': datetime.now().isoformat(),
            
            # Scores principaux
            'ai_score': ai_score,
            'plagiarism_score': plagiarism_score,
            'risk_level': risk_level,
            
            # Détails des analyses
            'ai_analysis': {
                'method': 'gptzero_api',
                'success': ai_result.get('success', False),
                'details': ai_result.get('details', {}),
                'sentences': ai_result.get('sentences', [])
            },
            
            'plagiarism_analysis': {
                'method': 'local_hybrid',
                'success': plagiarism_result.get('success', False),
                'matches': plagiarism_result.get('matches', []),
                'total_compared': plagiarism_result.get('total_compared', 0),
                'details': plagiarism_result.get('details', {})
            },
            
            # Informations du document
            'document_info': {
                'id': document.id,
                'filename': document.original_filename,
                'size': len(document.file_path) if document.file_path else 0
            },
            
            # Erreurs éventuelles
            'errors': errors,
            'partial_analysis': len(errors) > 0 and success
        }
    
    def _calculate_risk_level(self, ai_score: float, plagiarism_score: float) -> str:
        """Calculer le niveau de risque global"""
        max_score = max(ai_score, plagiarism_score)
        
        if max_score >= 80:
            return 'HIGH'
        elif max_score >= 50:
            return 'MEDIUM'
        elif max_score >= 20:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _save_analysis_results(self, document: Document, results: Dict, original_text: str):
        """Sauvegarder les résultats d'analyse en base de données"""
        try:
            # Créer l'enregistrement principal
            analysis_result = AnalysisResult()
            analysis_result.document_id = document.id
            analysis_result.ai_score = results.get('ai_score', 0)
            analysis_result.plagiarism_score = results.get('plagiarism_score', 0)
            analysis_result.raw_results = results
            analysis_result.created_at = datetime.now()
            
            db.session.add(analysis_result)
            db.session.flush()  # Pour obtenir l'ID
            
            # Sauvegarder les phrases surlignées pour l'IA
            ai_sentences = results.get('ai_analysis', {}).get('sentences', [])
            self._save_highlighted_sentences(document, ai_sentences, 'ai', original_text)
            
            # Sauvegarder les correspondances de plagiat
            plagiarism_matches = results.get('plagiarism_analysis', {}).get('matches', [])
            self._save_plagiarism_matches(document, plagiarism_matches, original_text)
            
            db.session.commit()
            self.logger.info(f"Résultats sauvegardés pour document {document.id}")
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Erreur lors de la sauvegarde : {e}")
    
    def _save_highlighted_sentences(self, document: Document, sentences: list, sentence_type: str, original_text: str):
        """Sauvegarder les phrases surlignées"""
        try:
            for sentence_data in sentences:
                if isinstance(sentence_data, dict):
                    sentence_text = sentence_data.get('text', '')
                    confidence = sentence_data.get('confidence', 0)
                elif isinstance(sentence_data, str):
                    sentence_text = sentence_data
                    confidence = 0.5
                else:
                    continue
                
                if sentence_text and sentence_text in original_text:
                    highlighted_sentence = HighlightedSentence()
                    highlighted_sentence.document_id = document.id
                    highlighted_sentence.sentence_text = sentence_text
                    highlighted_sentence.is_ai_generated = (sentence_type == 'ai')
                    highlighted_sentence.start_position = original_text.find(sentence_text)
                    highlighted_sentence.end_position = original_text.find(sentence_text) + len(sentence_text)
                    db.session.add(highlighted_sentence)
                    
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde phrases surlignées : {e}")
    
    def _save_plagiarism_matches(self, document: Document, matches: list, original_text: str):
        """Sauvegarder les correspondances de plagiat"""
        try:
            for match in matches[:5]:  # Limiter aux 5 meilleures correspondances
                matched_text = match.get('matched_text', '')
                source_text = match.get('source_text', '')
                similarity = match.get('similarity', 0)
                
                if matched_text and matched_text in original_text:
                    highlighted_sentence = HighlightedSentence()
                    highlighted_sentence.document_id = document.id
                    highlighted_sentence.sentence_text = matched_text
                    highlighted_sentence.is_plagiarism = True
                    highlighted_sentence.start_position = original_text.find(matched_text)
                    highlighted_sentence.end_position = original_text.find(matched_text) + len(matched_text)
                    db.session.add(highlighted_sentence)
                    
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde correspondances plagiat : {e}")
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Créer un résultat d'erreur standardisé"""
        return {
            'success': False,
            'ai_score': 0,
            'plagiarism_score': 0,
            'analysis_method': 'hybrid_error',
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtenir le statut des services"""
        return {
            'hybrid_service': True,
            'ai_detection': {
                'provider': 'GPTZero API',
                'status': 'active',
                'method': 'cloud_api'
            },
            'plagiarism_detection': {
                'provider': 'Local Processing',
                'status': 'active',
                'method': 'tfidf_sentence_transformer',
                'database_stats': self.local_plagiarism.get_database_stats()
            }
        }

# Instance globale du service hybride
hybrid_analysis_service = HybridAnalysisService()