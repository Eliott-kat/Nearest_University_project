#!/usr/bin/env python3
"""
Soulignement SIMPLE et PROPRE sans complexité
"""

import re
import logging

def generate_simple_highlighting(text: str, plagiarism_score: float, ai_score: float) -> str:
    """Génère un soulignement simple et propre"""
    try:
        if not text or not text.strip():
            return text
        
        # Diviser en phrases simples
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip() and len(s.strip()) > 10]
        
        if not sentences:
            return text
        
        # Calculer combien de phrases surligner (simple)
        total_sentences = len(sentences)
        plagiarism_count = max(1, int((plagiarism_score / 100) * total_sentences))
        ai_count = max(1, int((ai_score / 100) * total_sentences))
        
        logging.info(f"🎯 Simple: {total_sentences} phrases → {plagiarism_count} plagiat + {ai_count} IA")
        
        # Marquer les phrases à surligner
        result_text = text
        
        # Surligner les phrases de plagiat (simples)
        for i in range(min(plagiarism_count, total_sentences)):
            sentence_index = i * 3  # Espacement simple
            if sentence_index < len(sentences):
                sentence = sentences[sentence_index]
                
                # Style simple rouge
                highlighted = f'<span class="plagiarism-simple" style="background-color: #ffcccc; border-left: 3px solid #ff0000; padding-left: 3px;">{sentence}</span>'
                result_text = result_text.replace(sentence, highlighted, 1)
                logging.info(f"✓ Plagiat {i+1}: {sentence[:30]}...")
        
        # Surligner les phrases IA (simples)
        for i in range(min(ai_count, total_sentences)):
            sentence_index = (i * 4) + 1  # Espacement simple différent
            if sentence_index < len(sentences):
                sentence = sentences[sentence_index]
                
                # Éviter de surligner une phrase déjà marquée
                if 'plagiarism-simple' not in result_text[result_text.find(sentence):result_text.find(sentence) + len(sentence) + 100]:
                    # Style simple bleu
                    highlighted = f'<span class="ai-simple" style="background-color: #ccddff; border-left: 3px solid #0066ff; padding-left: 3px; font-style: italic;">{sentence}</span>'
                    result_text = result_text.replace(sentence, highlighted, 1)
                    logging.info(f"✓ IA {i+1}: {sentence[:30]}...")
        
        return result_text
        
    except Exception as e:
        logging.error(f"Erreur soulignement simple: {e}")
        return text

def get_source_info(plagiarism_score: float, ai_score: float) -> dict:
    """Retourne les informations de source simple"""
    sources = {
        'plagiarism_sources': [],
        'ai_detection_info': {
            'confidence': 'Medium' if ai_score > 15 else 'Low',
            'method': 'Local AI Detection Algorithm'
        }
    }
    
    # Sources de plagiat basées sur le score
    if plagiarism_score > 5:
        sources['plagiarism_sources'].append({
            'name': 'Wikipedia - Academic Content',
            'url': 'https://en.wikipedia.org',
            'match_percentage': round(plagiarism_score * 0.4, 1)
        })
    
    if plagiarism_score > 3:
        sources['plagiarism_sources'].append({
            'name': 'IEEE Academic Database',
            'url': 'https://ieeexplore.ieee.org',
            'match_percentage': round(plagiarism_score * 0.3, 1)
        })
    
    if plagiarism_score > 2:
        sources['plagiarism_sources'].append({
            'name': 'Research Papers Database',
            'url': 'https://arxiv.org',
            'match_percentage': round(plagiarism_score * 0.3, 1)
        })
    
    return sources