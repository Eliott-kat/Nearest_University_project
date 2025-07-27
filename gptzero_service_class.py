"""
GPTZero Service Class - Compatible with UnifiedPlagiarismService
"""
import os
import requests
import logging
from typing import Dict, Any, Optional

class GPTZeroService:
    """Service class pour GPTZero compatible avec le système existant"""
    
    def __init__(self):
        self.api_key = os.environ.get('GPTZERO_API_KEY')
        self.base_url = "https://api.gptzero.me/v2"
        
    def is_configured(self) -> bool:
        """Vérifie si GPTZero est configuré"""
        return bool(self.api_key)
    
    def authenticate(self) -> bool:
        """Test d'authentification GPTZero"""
        if not self.is_configured():
            return False
            
        try:
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Test simple avec un petit texte
            response = requests.post(
                f"{self.base_url}/predict/text",
                headers=headers,
                json={"document": "This is a test document for authentication."},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"Erreur authentification GPTZero: {str(e)}")
            return False
    
    def submit_document(self, document) -> Optional[str]:
        """Soumet un document à GPTZero et retourne l'ID"""
        if not self.is_configured():
            return None
            
        try:
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                "document": document.content,
                "multilingual": True,
                "check_plagiarism": True
            }
            
            response = requests.post(
                f"{self.base_url}/predict/text",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                # GPTZero retourne le résultat immédiatement
                document.copyleaks_id = f"gptzero_{document.id}"
                return document.copyleaks_id
                
        except Exception as e:
            logging.error(f"Erreur soumission GPTZero: {str(e)}")
            
        return None
    
    def get_analysis_results(self, document) -> Optional[Dict[str, Any]]:
        """Récupère les résultats d'analyse (immédiat avec GPTZero)"""
        if not document.copyleaks_id or not document.copyleaks_id.startswith('gptzero_'):
            return None
            
        try:
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                "document": document.content,
                "multilingual": True,
                "check_plagiarism": True
            }
            
            response = requests.post(
                f"{self.base_url}/predict/text",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._format_results(result)
                
        except Exception as e:
            logging.error(f"Erreur récupération résultats GPTZero: {str(e)}")
            
        return None
    
    def _format_results(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Formate les résultats GPTZero au format standard"""
        try:
            documents = raw_result.get('documents', [{}])
            if not documents:
                return None
                
            doc = documents[0]
            class_probs = doc.get('class_probabilities', {})
            sentences = doc.get('sentences', [])
            
            # Calculer les scores
            ai_score = round(class_probs.get('ai', 0.0) * 100, 1)
            plagiarism_score = self._estimate_plagiarism_score(class_probs)
            
            # Formater les phrases suspectes
            highlighted_sentences = []
            for sentence in sentences:
                sentence_ai_prob = sentence.get('class_probabilities', {}).get('ai', 0.0)
                if sentence_ai_prob > 0.5:  # Seuil de détection
                    highlighted_sentences.append({
                        'text': sentence.get('sentence', ''),
                        'type': 'ai_generated' if sentence_ai_prob > 0.7 else 'suspicious',
                        'confidence': round(sentence_ai_prob, 3),
                        'explanation': f'IA détectée: {round(sentence_ai_prob * 100, 1)}%'
                    })
            
            return {
                'ai_percentage': ai_score,
                'plagiarism_percentage': plagiarism_score,
                'overall_similarity': max(ai_score, plagiarism_score),
                'highlighted_sentences': highlighted_sentences,
                'provider': 'GPTZero',
                'confidence': doc.get('confidence_category', 'medium'),
                'raw_response': raw_result
            }
            
        except Exception as e:
            logging.error(f"Erreur formatage GPTZero: {str(e)}")
            return None
    
    def _estimate_plagiarism_score(self, class_probs: Dict[str, float]) -> float:
        """Estime le score de plagiat basé sur les probabilités"""
        # GPTZero focus sur l'IA, estimation du plagiat basée sur 'mixed' content
        mixed_prob = class_probs.get('mixed', 0.0)
        return round(mixed_prob * 25, 1)  # Estimation conservative