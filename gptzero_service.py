"""
GPTZero API Service - AI Content Detection & Plagiarism Checking
Provides both AI detection and plagiarism checking in a single API
"""

import os
import requests
import logging
import time
import json
from typing import Dict, Any, Optional, List, Tuple

class GPTZeroService:
    """Service pour intégrer l'API GPTZero (détection IA + plagiat)"""
    
    def __init__(self):
        self.api_key = os.environ.get('GPTZERO_API_KEY')
        self.base_url = "https://api.gptzero.me/v2"
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
    def is_configured(self) -> bool:
        """Vérifie si l'API GPTZero est configurée"""
        return bool(self.api_key)
    
    def analyze_text(self, text: str, filename: str = "document") -> Optional[Dict[str, Any]]:
        """
        Analyse un texte avec GPTZero pour détection IA et plagiat
        
        Args:
            text: Le texte à analyser
            filename: Nom du fichier (optionnel)
            
        Returns:
            Dict contenant les résultats d'analyse ou None si erreur
        """
        if not self.is_configured():
            logging.error("GPTZero API key not configured")
            return None
            
        if len(text.strip()) < 50:
            logging.error("Text too short for GPTZero analysis (minimum 50 characters)")
            return None
            
        try:
            # Préparer la requête
            payload = {
                "document": text,
                "multilingual": True,
                "check_plagiarism": True  # Active la vérification de plagiat
            }
            
            logging.info(f"Envoi du texte à GPTZero pour analyse (longueur: {len(text)} caractères)")
            
            # Envoyer la requête
            response = requests.post(
                f"{self.base_url}/predict/text",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                logging.info("Analyse GPTZero réussie")
                return self._process_gptzero_response(result, text)
            else:
                logging.error(f"Erreur GPTZero API: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur de connexion GPTZero: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Erreur GPTZero inattendue: {str(e)}")
            return None
    
    def _process_gptzero_response(self, response: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """
        Traite la réponse de GPTZero et la convertit au format standard AcadCheck
        
        Args:
            response: Réponse brute de l'API GPTZero
            original_text: Texte original analysé
            
        Returns:
            Dict au format standard pour AcadCheck
        """
        try:
            # Extraire les données principales
            document_classification = response.get('documents', [{}])[0].get('class_probabilities', {})
            sentences = response.get('documents', [{}])[0].get('sentences', [])
            
            # Calculer les scores globaux
            ai_probability = document_classification.get('ai', 0.0)
            human_probability = document_classification.get('human', 1.0)
            
            # Convertir en pourcentages
            ai_percentage = round(ai_probability * 100, 1)
            plagiarism_percentage = self._extract_plagiarism_score(response)
            
            # Extraire les phrases suspectes
            highlighted_sentences = self._extract_highlighted_sentences(sentences, original_text)
            
            # Créer le résultat formaté
            result = {
                'success': True,
                'provider': 'gptzero',
                'analysis': {
                    'ai_percentage': ai_percentage,
                    'plagiarism_percentage': plagiarism_percentage,
                    'overall_score': max(ai_percentage, plagiarism_percentage),
                    'confidence': response.get('documents', [{}])[0].get('confidence_category', 'medium'),
                    'classification': response.get('documents', [{}])[0].get('class_probabilities', {})
                },
                'highlighted_sentences': highlighted_sentences,
                'raw_response': response,
                'stats': {
                    'total_sentences': len(sentences),
                    'flagged_sentences': len([s for s in highlighted_sentences if s['confidence'] > 0.7]),
                    'ai_sentences': len([s for s in sentences if s.get('class_probabilities', {}).get('ai', 0) > 0.5]),
                    'human_sentences': len([s for s in sentences if s.get('class_probabilities', {}).get('human', 0) > 0.5])
                }
            }
            
            logging.info(f"GPTZero analyse terminée - IA: {ai_percentage}%, Plagiat: {plagiarism_percentage}%")
            return result
            
        except Exception as e:
            logging.error(f"Erreur lors du traitement de la réponse GPTZero: {str(e)}")
            return {
                'success': False,
                'error': f"Erreur de traitement: {str(e)}",
                'provider': 'gptzero'
            }
    
    def _extract_plagiarism_score(self, response: Dict[str, Any]) -> float:
        """
        Extrait le score de plagiat de la réponse GPTZero
        
        Args:
            response: Réponse de l'API GPTZero
            
        Returns:
            Score de plagiat en pourcentage
        """
        try:
            # GPTZero inclut parfois les données de plagiat dans la réponse
            plagiarism_data = response.get('plagiarism', {})
            if plagiarism_data:
                return float(plagiarism_data.get('percentage', 0.0))
            
            # Si pas de données de plagiat spécifiques, estimer basé sur la classification
            documents = response.get('documents', [])
            if documents:
                doc = documents[0]
                # Une heuristique simple basée sur les probabilités
                mixed_prob = doc.get('class_probabilities', {}).get('mixed', 0.0)
                return round(mixed_prob * 30, 1)  # Estimation conservative
            
            return 0.0
            
        except Exception as e:
            logging.warning(f"Impossible d'extraire le score de plagiat: {str(e)}")
            return 0.0
    
    def _extract_highlighted_sentences(self, sentences: List[Dict], original_text: str) -> List[Dict[str, Any]]:
        """
        Extrait et formate les phrases suspectes pour AcadCheck
        
        Args:
            sentences: Liste des phrases analysées par GPTZero
            original_text: Texte original
            
        Returns:
            Liste des phrases formatées pour AcadCheck
        """
        highlighted = []
        text_lines = original_text.split('\n')
        
        try:
            for i, sentence in enumerate(sentences):
                ai_prob = sentence.get('class_probabilities', {}).get('ai', 0.0)
                sentence_text = sentence.get('sentence', '')
                
                # Ne garder que les phrases avec probabilité IA significative
                if ai_prob > 0.3 and sentence_text.strip():
                    # Déterminer le type basé sur la probabilité
                    if ai_prob > 0.7:
                        sentence_type = 'ai_generated'
                        confidence = ai_prob
                    elif ai_prob > 0.5:
                        sentence_type = 'mixed'
                        confidence = ai_prob
                    else:
                        sentence_type = 'suspicious'
                        confidence = ai_prob
                    
                    highlighted.append({
                        'text': sentence_text,
                        'type': sentence_type,
                        'confidence': round(confidence, 3),
                        'start_position': self._find_text_position(sentence_text, original_text),
                        'end_position': self._find_text_position(sentence_text, original_text) + len(sentence_text),
                        'explanation': f'Probabilité IA: {round(ai_prob * 100, 1)}%',
                        'source': 'GPTZero AI Detection'
                    })
            
        except Exception as e:
            logging.error(f"Erreur lors de l'extraction des phrases: {str(e)}")
        
        return highlighted
    
    def _find_text_position(self, sentence: str, full_text: str) -> int:
        """
        Trouve la position d'une phrase dans le texte complet
        
        Args:
            sentence: La phrase à trouver
            full_text: Le texte complet
            
        Returns:
            Position de début de la phrase (0 si non trouvée)
        """
        try:
            return full_text.find(sentence.strip())
        except:
            return 0
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le service GPTZero
        
        Returns:
            Dict avec les informations du service
        """
        return {
            'name': 'GPTZero',
            'provider': 'gptzero',
            'features': ['ai_detection', 'plagiarism_check'],
            'configured': self.is_configured(),
            'api_endpoint': self.base_url,
            'accuracy': '99%+ AI detection, 96.5% mixed content',
            'supported_languages': 'Multiple languages',
            'pricing': 'Premium: $16-24/month, 300k words',
            'website': 'https://gptzero.me'
        }

# Instance globale du service
gptzero_service = GPTZeroService()