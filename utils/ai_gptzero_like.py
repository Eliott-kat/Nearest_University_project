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
    
    def analyze_advanced_ai_patterns(self, text: str) -> Dict:
        """Analyse avancée des patterns IA supplémentaires"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return {'coherence_score': 0, 'vocabulary_diversity': 100, 'temporal_consistency': 0}
        
        # 1. COHÉRENCE THÉMATIQUE EXCESSIVE (IA reste sur le sujet)
        all_words = ' '.join(sentences).lower().split()
        word_freq = Counter(all_words)
        
        # Calculer concentration thématique
        top_words = [word for word, count in word_freq.most_common(10) if len(word) > 3]
        theme_concentration = sum(word_freq[word] for word in top_words) / len(all_words) * 100
        
        # 2. DIVERSITÉ LEXICALE (IA utilise vocabulaire limité mais sophistiqué)
        unique_words = len(set(all_words))
        total_words = len(all_words)
        vocabulary_diversity = (unique_words / total_words * 100) if total_words > 0 else 0
        
        # 3. CONSISTANCE TEMPORELLE (IA utilise toujours même temps)
        present_tense = len(re.findall(r'\b(is|are|has|have|does|do)\b', text.lower()))
        past_tense = len(re.findall(r'\b(was|were|had|did|went|came)\b', text.lower()))
        future_tense = len(re.findall(r'\b(will|shall|going to)\b', text.lower()))
        
        total_tense = present_tense + past_tense + future_tense
        if total_tense > 0:
            max_tense = max(present_tense, past_tense, future_tense)
            temporal_consistency = (max_tense / total_tense) * 100
        else:
            temporal_consistency = 0
        
        # 4. DÉTECTION DE FORMALITÉ EXCESSIVE
        formal_markers = len(re.findall(r'\b(thus|hence|therefore|furthermore|moreover|consequently|subsequently)\b', text.lower()))
        informal_markers = len(re.findall(r'\b(yeah|ok|well|you know|I think|maybe|probably)\b', text.lower()))
        
        formality_ratio = formal_markers / max(informal_markers + formal_markers, 1) * 100
        
        return {
            'theme_concentration': round(theme_concentration, 1),
            'vocabulary_diversity': round(vocabulary_diversity, 1),
            'temporal_consistency': round(temporal_consistency, 1),
            'formality_ratio': round(formality_ratio, 1)
        }
    
    def calculate_semantic_coherence(self, text: str) -> float:
        """Calcule la cohérence sémantique (IA = trop cohérent)"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) < 2:
            return 0
        
        # Analyser transitions entre phrases
        transition_words = [
            'however', 'furthermore', 'moreover', 'therefore', 'consequently',
            'subsequently', 'additionally', 'nevertheless', 'nonetheless'
        ]
        
        smooth_transitions = 0
        for i in range(1, len(sentences)):
            sentence = sentences[i].lower()
            if any(word in sentence for word in transition_words):
                smooth_transitions += 1
        
        # Score de cohérence (trop de transitions = IA)
        coherence_score = (smooth_transitions / max(len(sentences) - 1, 1)) * 100
        return min(coherence_score, 100)

    def detect_ai_gptzero_like(self, text: str, perplexity_thresh: float = 50, burstiness_thresh: float = 15) -> Dict:
        """Détection IA ultra-avancée style GPTZero avec 5+ métriques"""
        if len(text.strip()) < 50:
            return {
                'is_ai': False,
                'confidence': 0,
                'perplexity': 100,
                'burstiness': 0,
                'reason': 'Texte trop court pour analyse'
            }
        
        # Métriques principales GPTZero
        perplexity = self.calculate_simple_perplexity(text)
        burstiness = self.calculate_burstiness(text)
        patterns = self.analyze_sentence_patterns(text)
        
        # Nouvelles métriques avancées
        advanced_patterns = self.analyze_advanced_ai_patterns(text)
        semantic_coherence = self.calculate_semantic_coherence(text)
        
        # Seuils adaptatifs basés sur longueur du texte
        words_count = len(text.split())
        if words_count < 100:
            perplexity_thresh *= 0.8  # Plus strict pour textes courts
            burstiness_thresh *= 0.9
        elif words_count > 300:
            perplexity_thresh *= 1.2  # Plus permissif pour textes longs
            burstiness_thresh *= 1.1
        
        # Analyse des indicateurs IA
        indicators = []
        ai_score = 0
        
        # 1. Perplexité (25 points max)
        if perplexity < perplexity_thresh:
            perplexity_contribution = min((perplexity_thresh - perplexity) / perplexity_thresh * 25, 25)
            ai_score += perplexity_contribution
            indicators.append(f"Perplexité faible ({perplexity:.1f})")
        
        # 2. Burstiness (20 points max)
        if burstiness < burstiness_thresh:
            burstiness_contribution = min((burstiness_thresh - burstiness) / burstiness_thresh * 20, 20)
            ai_score += burstiness_contribution
            indicators.append(f"Faible variabilité phrases ({burstiness:.1f})")
        
        # 3. Uniformité des débuts (15 points max)
        if patterns['uniformity_score'] > 30:
            uniformity_contribution = min((patterns['uniformity_score'] - 30) / 70 * 15, 15)
            ai_score += uniformity_contribution
            indicators.append(f"Structures répétitives ({patterns['uniformity_score']:.1f}%)")
        
        # 4. Complexité syntaxique (15 points max)
        if patterns['avg_complexity'] > 1.5:
            complexity_contribution = min((patterns['avg_complexity'] - 1.5) / 3 * 15, 15)
            ai_score += complexity_contribution
            indicators.append(f"Complexité excessive ({patterns['avg_complexity']:.1f})")
        
        # 5. Cohérence sémantique (10 points max)
        if semantic_coherence > 40:
            coherence_contribution = min((semantic_coherence - 40) / 60 * 10, 10)
            ai_score += coherence_contribution
            indicators.append(f"Cohérence excessive ({semantic_coherence:.1f}%)")
        
        # 6. Concentration thématique (10 points max)
        if advanced_patterns['theme_concentration'] > 25:
            theme_contribution = min((advanced_patterns['theme_concentration'] - 25) / 75 * 10, 10)
            ai_score += theme_contribution
            indicators.append(f"Concentration thématique ({advanced_patterns['theme_concentration']:.1f}%)")
        
        # 7. Formalité excessive (5 points max)
        if advanced_patterns['formality_ratio'] > 60:
            formality_contribution = min((advanced_patterns['formality_ratio'] - 60) / 40 * 5, 5)
            ai_score += formality_contribution
            indicators.append(f"Formalité excessive ({advanced_patterns['formality_ratio']:.1f}%)")
        
        # Score final
        confidence = min(ai_score, 100)
        is_ai = confidence >= 45  # Seuil adaptatif
        
        reason = " + ".join(indicators) if indicators else "Indicateurs humains naturels détectés"
        
        return {
            'is_ai': is_ai,
            'confidence': round(confidence, 1),
            'perplexity': round(perplexity, 1),
            'burstiness': round(burstiness, 1),
            'uniformity_score': round(patterns['uniformity_score'], 1),
            'complexity_score': round(patterns['avg_complexity'], 1),
            'semantic_coherence': round(semantic_coherence, 1),
            'theme_concentration': advanced_patterns['theme_concentration'],
            'vocabulary_diversity': advanced_patterns['vocabulary_diversity'],
            'formality_ratio': advanced_patterns['formality_ratio'],
            'reason': reason,
            'method': 'ultra_advanced_gptzero_analysis',
            'indicators_detected': len(indicators)
        }

# Instance globale
gptzero_detector = GPTZeroLikeDetector()

def detect_ai_gptzero_like(text: str, perplexity_thresh: float = 50, burstiness_thresh: float = 15) -> Dict:
    """Interface publique pour détection GPTZero-like"""
    return gptzero_detector.detect_ai_gptzero_like(text, perplexity_thresh, burstiness_thresh)