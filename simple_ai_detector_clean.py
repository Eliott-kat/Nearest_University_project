"""
Détecteur IA simple mais très efficace - Version propre
Gamme élargie 0-90% avec reconnaissance du contenu académique authentique
"""

import os
import logging
import re
from typing import Dict, List

class SimpleAIDetector:
    """Détecteur IA avec gamme élargie et reconnaissance académique"""
    
    def __init__(self):
        self.ai_vocabulary = {
            # Vocabulaire IA fort (poids élevé)
            'furthermore': 4.0, 'moreover': 4.0, 'additionally': 3.5, 'subsequently': 4.0,
            'consequently': 3.0, 'nonetheless': 3.5, 'nevertheless': 3.5,
            'optimization': 2.5, 'methodology': 2.5, 'comprehensive': 2.0, 'systematic': 2.0,
            'sophisticated': 2.5, 'substantial': 1.5, 'significant': 1.2, 'demonstrates': 1.8,
            'facilitates': 2.2, 'leverages': 2.5, 'enhances': 1.5, 'optimal': 2.0
        }
        
        self.human_vocabulary = {
            # Vocabulaire humain (réduit le score IA)
            'i think': -4.0, 'i believe': -4.0, 'in my opinion': -5.0, 'personally': -4.0,
            'honestly': -3.5, 'from my experience': -5.0, 'my family': -4.0, 'my friends': -4.0,
            "don't": -2.5, "can't": -2.5, "won't": -2.5, "it's": -2.0, "i'm": -2.5,
            'love': -3.0, 'hate': -4.0, 'awesome': -4.0, 'cool': -2.5, 'weird': -2.5
        }
        
        logging.info("✅ Détecteur IA simple initialisé")
    
    def detect_ai_content(self, text: str) -> Dict:
        """Détection IA avec gamme élargie 0-90%"""
        try:
            text_clean = self._preprocess_text(text)
            sentences = self._split_sentences(text_clean)
            
            if len(sentences) == 0:
                return {'ai_probability': 0.0, 'confidence': 'low'}
            
            # Calcul du score base
            vocab_score = self._analyze_vocabulary(text_clean)
            pattern_score = self._analyze_patterns(text_clean)
            formality_score = self._analyze_formality(text_clean, sentences)
            
            # Combinaison pondérée
            total_score = (vocab_score * 0.4 + pattern_score * 0.35 + formality_score * 0.25)
            
            # Normalisation pour gamme élargie 0-90%
            normalized_score = min(max(total_score, 0), 90)
            
            # Réduction pour contenu académique authentique
            if self._is_authentic_academic(text_clean):
                normalized_score *= 0.6  # Réduction importante
            
            # Déterminer confiance
            confidence = 'high' if normalized_score < 20 or normalized_score > 70 else 'medium'
            
            return {
                'ai_probability': round(normalized_score, 1),
                'confidence': confidence,
                'method_used': 'enhanced_simple_detector'
            }
            
        except Exception as e:
            logging.error(f"Erreur détection IA: {e}")
            return {'ai_probability': 20.0, 'confidence': 'low'}
    
    def _analyze_vocabulary(self, text: str) -> float:
        """Analyse du vocabulaire avec gamme élargie"""
        text_lower = text.lower()
        words = text_lower.split()
        
        if not words:
            return 0
        
        ai_score = sum(weight for word, weight in self.ai_vocabulary.items() if word in text_lower)
        human_score = sum(abs(weight) for word, weight in self.human_vocabulary.items() if word in text_lower)
        
        # Score combiné
        combined = max(0, ai_score - human_score * 0.8)
        
        # Normalisation pour gamme élargie
        return min((combined / len(words)) * 800, 90)
    
    def _analyze_patterns(self, text: str) -> float:
        """Analyse des patterns IA spécifiques"""
        score = 0
        text_lower = text.lower()
        
        # Patterns GPT caractéristiques
        gpt_patterns = [
            r'furthermore.*demonstrates',
            r'moreover.*comprehensive',
            r'additionally.*systematic',
            r'consequently.*substantial'
        ]
        
        for pattern in gpt_patterns:
            matches = len(re.findall(pattern, text_lower))
            score += matches * 25  # Score élevé pour patterns GPT
        
        # Transitions formelles excessives
        formal_transitions = ['furthermore', 'moreover', 'additionally', 'consequently']
        transition_count = sum(1 for trans in formal_transitions if trans in text_lower)
        
        if len(text_lower.split()) > 0:
            transition_density = (transition_count / len(text_lower.split())) * 100
            score += min(transition_density * 15, 40)
        
        return min(score, 90)
    
    def _analyze_formality(self, text: str, sentences: List[str]) -> float:
        """Analyse de la formalité excessive"""
        if not sentences:
            return 0
        
        score = 0
        text_lower = text.lower()
        
        # Mots formels excessifs
        formal_words = ['demonstrates', 'facilitates', 'encompasses', 'optimization', 
                       'methodology', 'systematic', 'comprehensive', 'sophisticated']
        
        formal_count = sum(1 for word in formal_words if word in text_lower)
        word_count = len(text_lower.split())
        
        if word_count > 0:
            formality_ratio = (formal_count / word_count) * 100
            score += min(formality_ratio * 12, 50)
        
        # Cohérence stylistique suspecte
        if len(sentences) > 3:
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_length > 25:  # Phrases très longues
                score += min((avg_length - 25) * 2, 30)
        
        return min(score, 90)
    
    def _is_authentic_academic(self, text: str) -> bool:
        """Détecte le contenu académique authentique"""
        text_lower = text.lower()
        
        # Indicateurs d'authenticité
        authentic_indicators = [
            'i would like to thank',
            'graduation project', 
            'my sincere gratitude',
            'my family and friends',
            'this journey',
            'near east university',
            'working on this project',
            'acknowledgement'
        ]
        
        return sum(1 for indicator in authentic_indicators if indicator in text_lower) >= 2
    
    def _preprocess_text(self, text: str) -> str:
        """Prétraite le texte"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Divise en phrases"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]