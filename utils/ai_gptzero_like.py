"""
Implémentation GPTZero-like pour détection IA basée sur perplexité et burstiness
Version simplifiée sans transformers pour compatibilité
"""

import re
import math
from collections import Counter
from typing import Dict, List

class GPTZeroLikeDetector:
    """Détecteur IA basé sur les principes GPTZero (perplexité + burstiness)"""
    
    def __init__(self):
        # Vocabulaire de base pour calcul de perplexité simplifiée
        self.common_words = {
            'the', 'and', 'a', 'to', 'of', 'in', 'is', 'it', 'that', 'for',
            'with', 'as', 'on', 'be', 'at', 'by', 'this', 'have', 'from',
            'or', 'one', 'had', 'but', 'not', 'what', 'all', 'were', 'we',
            'when', 'your', 'can', 'said', 'there', 'each', 'which', 'she',
            'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about',
            'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
            'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more'
        }
        
        # Mots typiques d'IA avec probabilités élevées
        self.ai_predictable_words = {
            'furthermore', 'subsequently', 'therefore', 'however', 'moreover',
            'nevertheless', 'comprehensive', 'significant', 'substantial',
            'implementation', 'optimization', 'methodology', 'framework',
            'demonstrates', 'indicates', 'reveals', 'facilitate', 'enhance',
            'efficient', 'effective', 'systematic', 'empirical', 'analysis'
        }
    
    def calculate_simple_perplexity(self, text: str) -> float:
        """Calcule une perplexité simplifiée basée sur la prévisibilité des mots"""
        words = re.findall(r'\b\w+\b', text.lower())
        if len(words) < 5:
            return 100  # Texte trop court
        
        # Compter les mots
        word_counts = Counter(words)
        total_words = len(words)
        
        # Calculer "surprise" pour chaque mot
        surprise_scores = []
        
        for i in range(1, len(words)):
            current_word = words[i]
            prev_word = words[i-1]
            
            # Score basé sur la fréquence du mot
            frequency_score = word_counts[current_word] / total_words
            
            # Bonus si mot très commun (prévisible)
            if current_word in self.common_words:
                frequency_score *= 2
            
            # Malus si mot typique IA (très prévisible dans contexte IA)
            if current_word in self.ai_predictable_words:
                frequency_score *= 3
            
            # Calculer "surprise" (inverse de prévisibilité)
            surprise = -math.log(max(frequency_score, 0.001))
            surprise_scores.append(surprise)
        
        # Perplexité moyenne
        avg_surprise = sum(surprise_scores) / len(surprise_scores)
        perplexity = math.exp(avg_surprise)
        
        return min(perplexity, 200)  # Cap à 200
    
    def calculate_burstiness(self, text: str) -> float:
        """Calcule la burstiness (variabilité de longueur des phrases)"""
        # Diviser en phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
        
        if len(sentences) < 2:
            return 0
        
        # Compter mots par phrase
        word_counts = [len(s.split()) for s in sentences]
        
        # Calculer écart-type manuel (équivalent numpy.std)
        mean_length = sum(word_counts) / len(word_counts)
        variance = sum((x - mean_length) ** 2 for x in word_counts) / len(word_counts)
        std_dev = math.sqrt(variance)
        
        return std_dev
    
    def analyze_sentence_patterns(self, text: str) -> Dict:
        """Analyse les patterns de phrases typiques IA"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return {'uniformity_score': 0, 'avg_complexity': 0}
        
        # Analyser uniformité des débuts de phrases
        sentence_starters = []
        for sentence in sentences:
            words = sentence.split()[:3]  # 3 premiers mots
            if len(words) >= 2:
                sentence_starters.append(' '.join(words[:2]).lower())
        
        # Calculer diversité des débuts
        unique_starters = len(set(sentence_starters))
        total_starters = len(sentence_starters)
        uniformity_score = (total_starters - unique_starters) / max(total_starters, 1) * 100
        
        # Complexité syntaxique moyenne
        complexity_scores = []
        for sentence in sentences:
            # Compter subordonnées, conjonctions, etc.
            subordinates = len(re.findall(r'\b(that|which|when|where|while|although|because|since|if)\b', sentence.lower()))
            conjunctions = len(re.findall(r'\b(furthermore|moreover|however|therefore|subsequently|nevertheless)\b', sentence.lower()))
            
            complexity = subordinates + conjunctions * 2
            complexity_scores.append(complexity)
        
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        
        return {
            'uniformity_score': uniformity_score,
            'avg_complexity': avg_complexity
        }
    
    def detect_ai_gptzero_like(self, text: str, perplexity_thresh: float = 50, burstiness_thresh: float = 15) -> Dict:
        """Détection IA style GPTZero avec métriques avancées"""
        if len(text.strip()) < 50:
            return {
                'is_ai': False,
                'confidence': 0,
                'perplexity': 100,
                'burstiness': 0,
                'reason': 'Texte trop court pour analyse'
            }
        
        # Calculer métriques principales
        perplexity = self.calculate_simple_perplexity(text)
        burstiness = self.calculate_burstiness(text)
        patterns = self.analyze_sentence_patterns(text)
        
        # Décision basée sur seuils GPTZero
        low_perplexity = perplexity < perplexity_thresh
        low_burstiness = burstiness < burstiness_thresh
        high_uniformity = patterns['uniformity_score'] > 30
        high_complexity = patterns['avg_complexity'] > 1.5
        
        # Score de confiance IA
        ai_indicators = 0
        if low_perplexity:
            ai_indicators += 30
        if low_burstiness:
            ai_indicators += 25
        if high_uniformity:
            ai_indicators += 25
        if high_complexity:
            ai_indicators += 20
        
        is_ai = ai_indicators >= 50
        confidence = min(ai_indicators, 100)
        
        # Raison détaillée
        reasons = []
        if low_perplexity:
            reasons.append(f"Perplexité faible ({perplexity:.1f})")
        if low_burstiness:
            reasons.append(f"Faible variabilité phrases ({burstiness:.1f})")
        if high_uniformity:
            reasons.append(f"Débuts phrases répétitifs ({patterns['uniformity_score']:.1f}%)")
        if high_complexity:
            reasons.append(f"Complexité syntaxique élevée ({patterns['avg_complexity']:.1f})")
        
        reason = " + ".join(reasons) if reasons else "Indicateurs humains détectés"
        
        return {
            'is_ai': is_ai,
            'confidence': confidence,
            'perplexity': round(perplexity, 1),
            'burstiness': round(burstiness, 1),
            'uniformity_score': round(patterns['uniformity_score'], 1),
            'complexity_score': round(patterns['avg_complexity'], 1),
            'reason': reason,
            'method': 'gptzero_like_analysis'
        }

# Instance globale
gptzero_detector = GPTZeroLikeDetector()

def detect_ai_gptzero_like(text: str, perplexity_thresh: float = 50, burstiness_thresh: float = 15) -> Dict:
    """Interface publique pour détection GPTZero-like"""
    return gptzero_detector.detect_ai_gptzero_like(text, perplexity_thresh, burstiness_thresh)