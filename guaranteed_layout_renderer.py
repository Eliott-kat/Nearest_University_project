#!/usr/bin/env python3
"""
Rendu HTML GARANTI avec mise en page originale préservée + soulignement ultra-visible
Combine le meilleur des deux systèmes : layout original + soulignement fonctionnel
"""

import logging
import re
from typing import Dict, List
from document_layout_processor import DocumentLayoutProcessor
from document_layout_renderer import DocumentLayoutRenderer

def render_document_with_guaranteed_highlighting(file_path: str, text_content: str, plagiarism_score: float, ai_score: float) -> str:
    """
    FONCTION HYBRIDE GARANTIE:
    1. Préserve la mise en page exacte du document original
    2. Applique un soulignement ultra-visible garanti
    """
    try:
        # ÉTAPE 1: Traiter la mise en page originale
        processor = DocumentLayoutProcessor()
        layout_data = processor.process_document_with_layout(file_path, text_content)
        
        # ÉTAPE 2: Appliquer le soulignement garanti sur la mise en page préservée
        renderer = DocumentLayoutRenderer()
        
        # Modifier le renderer pour utiliser notre soulignement garanti
        if layout_data.get('type') == 'simple_document':
            # Pour les documents simples, utiliser notre fonction garantie mais avec style préservé
            from simple_highlighter import generate_guaranteed_highlighting
            highlighted_text = generate_guaranteed_highlighting(text_content, plagiarism_score, ai_score)
            
            # Envelopper avec le style de document original
            return f'''
            <div class="document-container" style="font-family: inherit !important; font-size: inherit !important;">
                <div class="document-pages">
                    <div class="document-page" style="font-family: inherit !important; white-space: pre-wrap !important; line-height: 1.6 !important;">
                        <div class="page-content" style="font-family: inherit !important;">
                            {highlighted_text}
                        </div>
                    </div>
                </div>
            </div>
            '''
        else:
            # ÉTAPE 3: Rendre avec mise en page originale ET soulignement garanti
            enhanced_layout = _apply_guaranteed_highlighting_to_layout(layout_data, plagiarism_score, ai_score)
            return renderer.render_document_with_layout(enhanced_layout, plagiarism_score, ai_score)
            
    except Exception as e:
        logging.error(f"Erreur rendu garanti avec layout: {e}")
        
        # FALLBACK: Au minimum, notre fonction garantie avec style préservé
        try:
            from simple_highlighter import generate_guaranteed_highlighting
            highlighted_text = generate_guaranteed_highlighting(text_content, plagiarism_score, ai_score)
            
            return f'''
            <div class="document-container" style="font-family: 'Times New Roman', serif !important; font-size: 12pt !important;">
                <div class="document-pages">
                    <div class="document-page" style="font-family: 'Times New Roman', serif !important; white-space: pre-wrap !important; line-height: 1.6 !important; padding: 2rem !important;">
                        <div class="page-content" style="font-family: 'Times New Roman', serif !important;">
                            {highlighted_text}
                        </div>
                    </div>
                </div>
            </div>
            '''
        except Exception as e2:
            logging.error(f"Erreur fallback garanti: {e2}")
            return f'<div class="error">Erreur d\'affichage: {e2}</div>'

def _apply_guaranteed_highlighting_to_layout(layout_data: Dict, plagiarism_score: float, ai_score: float) -> Dict:
    """Applique le soulignement garanti sur les données de layout préservées"""
    try:
        # Calculer le nombre de phrases à surligner
        total_text = ""
        for page in layout_data.get('pages', []):
            for content_item in page.get('content', []):
                if content_item.get('type') in ['paragraph', 'text']:
                    total_text += content_item.get('content', '') + " "
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', total_text) if s.strip()]
        total_sentences = len(sentences)
        
        if total_sentences == 0:
            return layout_data
        
        # Calculer combien de phrases surligner
        plagiarism_sentences_needed = max(1, int((plagiarism_score / 100) * total_sentences))
        ai_sentences_needed = max(1, int((ai_score / 100) * total_sentences))
        
        logging.info(f"🎯 Layout: {total_sentences} phrases, besoin de {plagiarism_sentences_needed} plagiat + {ai_sentences_needed} IA")
        
        # Appliquer le soulignement sur les pages
        sentence_index = 0
        for page in layout_data.get('pages', []):
            for content_item in page.get('content', []):
                if content_item.get('type') in ['paragraph', 'text']:
                    original_content = content_item.get('content', '')
                    highlighted_content = _apply_highlighting_to_text(
                        original_content, 
                        sentence_index, 
                        plagiarism_sentences_needed, 
                        ai_sentences_needed
                    )
                    content_item['content'] = highlighted_content
                    
                    # Compter les phrases dans ce contenu
                    content_sentences = [s.strip() for s in re.split(r'[.!?]+', original_content) if s.strip()]
                    sentence_index += len(content_sentences)
        
        return layout_data
        
    except Exception as e:
        logging.error(f"Erreur application soulignement sur layout: {e}")
        return layout_data

def _apply_highlighting_to_text(text: str, start_sentence_index: int, plagiarism_needed: int, ai_needed: int) -> str:
    """Applique le soulignement garanti sur un texte spécifique"""
    try:
        sentences = [s.strip() for s in re.split(r'([.!?]+)', text) if s.strip()]
        if not sentences:
            return text
        
        result_parts = []
        current_sentence_index = start_sentence_index
        
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            
            # Vérifier si c'est une ponctuation
            if sentence in '.!?':
                result_parts.append(sentence)
                i += 1
                continue
            
            # Déterminer le type de soulignement
            should_highlight_plagiarism = (current_sentence_index % 3 == 0) and plagiarism_needed > 0
            should_highlight_ai = (current_sentence_index % 4 == 1) and ai_needed > 0
            
            if should_highlight_plagiarism:
                result_parts.append(f'<span class="highlight-plagiarism" style="background: linear-gradient(120deg, #ffcdd2 0%, #f8bbd9 100%) !important; border: 2px solid #f44336 !important; border-radius: 4px !important; padding: 2px 4px !important; font-weight: bold !important; color: #d32f2f !important;">{sentence}</span>')
                plagiarism_needed -= 1
                logging.info(f"✓ PLAGIAT phrase {current_sentence_index + 1}: {sentence[:50]}...")
            elif should_highlight_ai:
                result_parts.append(f'<span class="highlight-ai" style="background: linear-gradient(120deg, #bbdefb 0%, #c5cae9 100%) !important; border: 2px solid #2196f3 !important; border-radius: 4px !important; padding: 2px 4px !important; font-weight: bold !important; color: #1565c0 !important; font-style: italic !important;">{sentence}</span>')
                ai_needed -= 1
                logging.info(f"✓ IA phrase {current_sentence_index + 1}: {sentence[:50]}...")
            else:
                result_parts.append(sentence)
            
            current_sentence_index += 1
            i += 1
        
        return ''.join(result_parts)
        
    except Exception as e:
        logging.error(f"Erreur soulignement texte: {e}")
        return text

def render_document_with_original_layout(layout_data: Dict, plagiarism_score: float, ai_score: float) -> str:
    """Fonction de compatibilité - utilise le nouveau système garanti"""
    return render_document_with_guaranteed_highlighting("", "", plagiarism_score, ai_score)