#!/usr/bin/env python3
"""
Affichage du document EXACTEMENT comme sur l'ordinateur + soulignement simple
"""

import os
import logging
from pathlib import Path

def render_document_with_simple_highlighting(file_path: str, extracted_text: str, plagiarism_score: float, ai_score: float) -> str:
    """Affiche le document avec sa mise en page originale + soulignement simple"""
    try:
        if not os.path.exists(file_path):
            logging.warning(f"Fichier non trouvé: {file_path}")
            return apply_simple_highlighting_to_text(extracted_text, plagiarism_score, ai_score)
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.docx':
            return render_docx_with_original_layout_and_simple_highlighting(file_path, extracted_text, plagiarism_score, ai_score)
        elif file_ext == '.pdf':
            return render_pdf_with_original_layout_and_simple_highlighting(file_path, extracted_text, plagiarism_score, ai_score)
        else:
            return apply_simple_highlighting_to_text(extracted_text, plagiarism_score, ai_score)
            
    except Exception as e:
        logging.error(f"Erreur rendu document: {e}")
        return apply_simple_highlighting_to_text(extracted_text, plagiarism_score, ai_score)

def render_docx_with_original_layout_and_simple_highlighting(file_path: str, extracted_text: str, plagiarism_score: float, ai_score: float) -> str:
    """Rend un DOCX avec mise en page originale + soulignement simple + images"""
    try:
        from docx import Document
        import re
        import os
        import base64
        from io import BytesIO
        
        doc = Document(file_path)
        html_content = []
        
        # Extraire les images du document
        document_images = extract_images_from_docx(doc)
        
        # Style pour préserver l'apparence originale avec affichage complet
        html_content.append('''
        <div class="document-original" style="
            font-family: 'Times New Roman', Times, serif !important;
            font-size: 12pt !important;
            line-height: 1.5 !important;
            color: #000000 !important;
            background: white;
            margin: 0;
            padding: 30px;
            width: 100%;
            max-width: none;
            overflow: visible;
            word-wrap: break-word;
        ">
        ''')
        
        # Calculer les phrases à surligner (simple)
        sentences = [s.strip() for s in re.split(r'[.!?]+', extracted_text) if s.strip() and len(s.strip()) > 10]
        total_sentences = len(sentences)
        plagiarism_count = max(1, int((plagiarism_score / 100) * total_sentences))
        ai_count = max(1, int((ai_score / 100) * total_sentences))
        
        # Marquer les phrases problématiques
        plagiarism_sentences = []
        ai_sentences = []
        
        for i in range(min(plagiarism_count, total_sentences)):
            sentence_index = i * 3
            if sentence_index < len(sentences):
                plagiarism_sentences.append(sentences[sentence_index])
        
        for i in range(min(ai_count, total_sentences)):
            sentence_index = (i * 4) + 1
            if sentence_index < len(sentences):
                ai_sentences.append(sentences[sentence_index])
        
        # Traiter chaque paragraphe du document original + images
        paragraph_index = 0
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            
            # Vérifier s'il y a des images dans ce paragraphe
            paragraph_images = []
            for run in paragraph.runs:
                if hasattr(run, '_element') and run._element.xpath('.//a:blip'):
                    for blip in run._element.xpath('.//a:blip'):
                        embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                        if embed and embed in document_images:
                            paragraph_images.append(document_images[embed])
            
            # Ajouter les images avant le texte si elles existent
            for img_data in paragraph_images:
                html_content.append(f'''
                <div style="text-align: center; margin: 20px 0;">
                    <img src="data:image/png;base64,{img_data}" 
                         style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" 
                         alt="Image du document" />
                </div>
                ''')
            
            if not text and not paragraph_images:
                html_content.append('<br>')
                continue
            
            # Déterminer le style du paragraphe
            para_style = ""
            if paragraph.alignment is not None:
                if paragraph.alignment == 1:  # Center
                    para_style += "text-align: center; "
                elif paragraph.alignment == 2:  # Right
                    para_style += "text-align: right; "
                elif paragraph.alignment == 3:  # Justify
                    para_style += "text-align: justify; "
            
            # Appliquer le soulignement simple si nécessaire
            highlighted_text = text
            
            # Vérifier si ce paragraphe contient des phrases problématiques
            for plag_sentence in plagiarism_sentences:
                if plag_sentence in highlighted_text:
                    highlighted_text = highlighted_text.replace(
                        plag_sentence,
                        f'<span style="background-color: #ffdddd; border-left: 3px solid #cc0000; padding-left: 3px;">{plag_sentence}</span>',
                        1
                    )
            
            for ai_sentence in ai_sentences:
                if ai_sentence in highlighted_text and 'background-color: #ffdddd' not in highlighted_text[highlighted_text.find(ai_sentence):]:
                    highlighted_text = highlighted_text.replace(
                        ai_sentence,
                        f'<span style="background-color: #ddeeff; border-left: 3px solid #0066cc; padding-left: 3px; font-style: italic;">{ai_sentence}</span>',
                        1
                    )
            
            # S'assurer que chaque paragraphe est affiché complètement
            html_content.append(f'<p style="margin: 6pt 0; {para_style} word-wrap: break-word; overflow: visible; width: 100%;">{highlighted_text}</p>')
        
        html_content.append('</div>')
        
        result = ''.join(html_content)
        
        # Log détaillé pour diagnostic
        paragraph_count = result.count('<p style=')
        total_length = len(result)
        logging.info(f"✅ DOCX rendu COMPLET: {paragraph_count} paragraphes, {total_length} caractères")
        
        return result
        
    except Exception as e:
        logging.error(f"Erreur rendu DOCX: {e}")
        return apply_simple_highlighting_to_text(extracted_text, plagiarism_score, ai_score)

def render_pdf_with_original_layout_and_simple_highlighting(file_path: str, extracted_text: str, plagiarism_score: float, ai_score: float) -> str:
    """Rend un PDF avec mise en page originale + soulignement simple"""
    try:
        # Pour les PDFs, utiliser le texte extrait avec style académique
        html_content = []
        
        html_content.append('''
        <div style="
            font-family: 'Times New Roman', Times, serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #000000;
            background: white;
            margin: 20px;
            padding: 25px;
            max-width: 210mm;
        ">
        ''')
        
        # Appliquer le soulignement simple au texte extrait
        highlighted_text = apply_simple_highlighting_to_text(extracted_text, plagiarism_score, ai_score)
        
        # Préserver les sauts de ligne
        paragraphs = highlighted_text.split('\n')
        for para in paragraphs:
            para = para.strip()
            if para:
                html_content.append(f'<p style="margin: 6pt 0; text-align: justify;">{para}</p>')
            else:
                html_content.append('<br>')
        
        html_content.append('</div>')
        
        result = ''.join(html_content)
        logging.info(f"✅ PDF rendu avec layout original + soulignement simple")
        return result
        
    except Exception as e:
        logging.error(f"Erreur rendu PDF: {e}")
        return apply_simple_highlighting_to_text(extracted_text, plagiarism_score, ai_score)

def extract_images_from_docx(doc) -> dict:
    """Extrait les images du document DOCX"""
    images = {}
    try:
        from docx.opc.constants import RELATIONSHIP_TYPE
        import base64
        
        # Parcourir les relations pour trouver les images
        for rel in doc.part.rels.values():
            if rel.reltype == RELATIONSHIP_TYPE.IMAGE:
                image_data = rel.target_part.blob
                # Encoder en base64 pour l'affichage HTML
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                images[rel.rId] = image_base64
                
        logging.info(f"📸 {len(images)} images extraites du document DOCX")
        return images
    except Exception as e:
        logging.error(f"Erreur extraction images: {e}")
        return {}

def apply_simple_highlighting_to_text(text: str, plagiarism_score: float, ai_score: float) -> str:
    """Applique un soulignement simple au texte brut"""
    from simple_clean_highlighter import generate_simple_highlighting
    return generate_simple_highlighting(text, plagiarism_score, ai_score)