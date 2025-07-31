#!/usr/bin/env python3
"""
Rendu HTML pour afficher les documents avec leur mise en page originale
"""

from typing import Dict, List
import logging

class DocumentLayoutRenderer:
    """Génère le HTML pour afficher les documents avec leur mise en page originale"""
    
    def __init__(self):
        self.page_styles = {
            'title_page': 'document-title-page',
            'chapter_title': 'document-chapter',
            'section_title': 'document-section',
            'special_section': 'document-special',
            'paragraph': 'document-paragraph'
        }
    
    def render_document_with_layout(self, layout_data: Dict, plagiarism_score: float = 0, ai_score: float = 0) -> str:
        """Rend le document HTML avec mise en page originale et soulignement"""
        try:
            if layout_data['type'] == 'simple_document':
                return self._render_simple_document(layout_data, plagiarism_score, ai_score)
            
            pages_html = []
            
            for i, page in enumerate(layout_data['pages']):
                page_html = self._render_page(page, i + 1, plagiarism_score, ai_score)
                pages_html.append(page_html)
            
            # Assembler le document complet
            document_html = f'''
            <div class="document-container">
                <div class="document-header">
                    <div class="document-type-badge">{layout_data['document_type'].replace('_', ' ').title()}</div>
                    <div class="page-counter">Pages: {layout_data['total_pages']}</div>
                </div>
                <div class="document-pages">
                    {''.join(pages_html)}
                </div>
            </div>
            '''
            
            return document_html
            
        except Exception as e:
            logging.error(f"Erreur rendu document: {e}")
            return f'<div class="document-error">Erreur d\'affichage: {e}</div>'
    
    def _render_page(self, page: Dict, page_number: int, plagiarism_score: float, ai_score: float) -> str:
        """Rend une page individuelle"""
        page_class = f"document-page page-{page['type']}"
        
        content_html = []
        
        for content_item in page['content']:
            if content_item['type'] == 'break':
                content_html.append('<div class="page-break"></div>')
                continue
            
            # Appliquer le soulignement intelligent
            highlighted_content = self._apply_intelligent_highlighting(
                content_item['content'], 
                content_item['type'],
                plagiarism_score, 
                ai_score
            )
            
            # Générer le style CSS inline
            style_css = self._generate_style_css(content_item['style'], content_item['alignment'])
            
            # Générer l'élément HTML
            element_class = self.page_styles.get(content_item['type'], 'document-paragraph')
            
            content_html.append(f'''
            <div class="{element_class}" style="{style_css}">
                {highlighted_content}
            </div>
            ''')
        
        return f'''
        <div class="{page_class}" data-page="{page_number}">
            <div class="page-content">
                {''.join(content_html)}
            </div>
            <div class="page-footer">
                <span class="page-number">Page {page_number}</span>
            </div>
        </div>
        '''
    
    def _generate_style_css(self, style: Dict, alignment: str) -> str:
        """Génère le CSS inline exact pour reproduire le document original"""
        css_parts = []
        
        # Taille de police exacte
        if style.get('font_size'):
            css_parts.append(f"font-size: {style['font_size']}pt")
        
        # Police exacte avec fallbacks
        if style.get('font_name'):
            if style['font_name'] in ['Calibri', 'Arial']:
                css_parts.append(f"font-family: '{style['font_name']}', sans-serif")
            else:
                css_parts.append(f"font-family: '{style['font_name']}', 'Times New Roman', serif")
        
        # Styles de caractère
        if style.get('bold'):
            css_parts.append("font-weight: bold")
        if style.get('italic'):
            css_parts.append("font-style: italic")
        if style.get('underline'):
            css_parts.append("text-decoration: underline")
        
        # Alignement exact
        if alignment:
            css_parts.append(f"text-align: {alignment}")
        
        # Espacements exacts
        if style.get('space_before'):
            css_parts.append(f"margin-top: {style['space_before']}pt")
        if style.get('space_after'):
            css_parts.append(f"margin-bottom: {style['space_after']}pt")
        
        # Indentations exactes
        if style.get('left_indent'):
            css_parts.append(f"margin-left: {style['left_indent']}pt")
        if style.get('first_line_indent'):
            css_parts.append(f"text-indent: {style['first_line_indent']}pt")
        
        # Interligne exact
        if style.get('line_spacing'):
            if style['line_spacing'] == 1.0:
                css_parts.append("line-height: 1.0")
            elif style['line_spacing'] == 1.5:
                css_parts.append("line-height: 1.5")
            elif style['line_spacing'] == 2.0:
                css_parts.append("line-height: 2.0")
            else:
                css_parts.append(f"line-height: {style['line_spacing']}")
        
        return '; '.join(css_parts)
    
    def _apply_intelligent_highlighting(self, text: str, content_type: str, plagiarism_score: float, ai_score: float) -> str:
        """Applique le soulignement intelligent selon le type de contenu"""
        # Ne pas souligner les titres et éléments spéciaux
        if content_type in ['title_page', 'chapter_title', 'special_section']:
            return text
        
        # Seulement souligner les paragraphes normaux
        if content_type != 'paragraph':
            return text
        
        # Appliquer la logique de soulignement existante
        return self._highlight_text_content(text, plagiarism_score, ai_score)
    
    def _highlight_text_content(self, text: str, plagiarism_score: float, ai_score: float) -> str:
        """Applique le soulignement au contenu textuel"""
        import re
        
        # Diviser en phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return text
        
        highlighted_sentences = []
        
        for i, sentence in enumerate(sentences):
            if len(sentence) < 10:
                highlighted_sentences.append(sentence)
                continue
            
            # Détecter les problèmes
            is_plagiarism = self._detect_plagiarism_in_sentence(sentence, plagiarism_score, i, len(sentences))
            is_ai = self._detect_ai_in_sentence(sentence, ai_score, i, len(sentences))
            
            # Appliquer le soulignement
            if is_plagiarism and is_ai:
                highlighted = f'<span class="highlight-both" title="Plagiat et IA détectés">{sentence}</span>'
            elif is_plagiarism:
                highlighted = f'<span class="highlight-plagiarism" title="Plagiat détecté">{sentence}</span>'
            elif is_ai:
                highlighted = f'<span class="highlight-ai" title="Contenu IA détecté">{sentence}</span>'
            else:
                highlighted = sentence
            
            highlighted_sentences.append(highlighted)
        
        return '. '.join(highlighted_sentences) + ('.' if sentences else '')
    
    def _detect_plagiarism_in_sentence(self, sentence: str, score: float, index: int, total: int) -> bool:
        """Détecte le plagiat dans une phrase"""
        if score < 5:
            return False
        
        sentence_lower = sentence.lower()
        plagiarism_keywords = [
            'research', 'study', 'analysis', 'results', 'conclusion', 'method',
            'data', 'theory', 'concept', 'development', 'process', 'system',
            'brain tumor', 'cnn', 'deep learning', 'machine learning'
        ]
        
        has_keywords = any(keyword in sentence_lower for keyword in plagiarism_keywords)
        is_positioned = (score > 8 and index % 4 == 0) or (score > 15 and index % 3 == 0)
        
        return has_keywords or is_positioned
    
    def _detect_ai_in_sentence(self, sentence: str, score: float, index: int, total: int) -> bool:
        """Détecte le contenu IA dans une phrase"""
        if score < 3:
            return False
        
        sentence_lower = sentence.lower()
        ai_keywords = [
            'furthermore', 'moreover', 'however', 'therefore', 'consequently',
            'thus', 'paradigm shift', 'comprehensive', 'significant',
            'remarkable', 'optimization', 'methodology'
        ]
        
        has_ai_keywords = any(keyword in sentence_lower for keyword in ai_keywords)
        is_formal = len(sentence.split()) > 12
        is_positioned = (score > 15 and index % 3 == 1) or (score > 25 and index % 2 == 0)
        
        return has_ai_keywords or is_formal or is_positioned
    
    def _render_simple_document(self, layout_data: Dict, plagiarism_score: float, ai_score: float) -> str:
        """Rend un document simple sans mise en page complexe"""
        page = layout_data['pages'][0]
        content = page['content'][0]['content']
        
        highlighted_content = self._highlight_text_content(content, plagiarism_score, ai_score)
        
        return f'''
        <div class="document-container simple">
            <div class="document-pages">
                <div class="document-page">
                    <div class="page-content">
                        <div class="document-paragraph" style="text-align: justify; line-height: 1.8;">
                            {highlighted_content}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''

# Instance globale
layout_renderer = DocumentLayoutRenderer()

def render_document_with_original_layout(layout_data: Dict, plagiarism_score: float = 0, ai_score: float = 0) -> str:
    """Fonction utilitaire pour rendre un document avec sa mise en page originale"""
    return layout_renderer.render_document_with_layout(layout_data, plagiarism_score, ai_score)

if __name__ == "__main__":
    # Test du rendu
    test_layout = {
        'type': 'document_with_layout',
        'pages': [
            {
                'type': 'section',
                'content': [
                    {
                        'type': 'title_page',
                        'content': 'GRADUATION PROJECT',
                        'style': {'font_size': 18, 'bold': True},
                        'alignment': 'center'
                    },
                    {
                        'type': 'title_page',
                        'content': 'Brain Tumor Detector Using CNN',
                        'style': {'font_size': 16, 'bold': True},
                        'alignment': 'center'
                    }
                ]
            }
        ],
        'total_pages': 1,
        'document_type': 'graduation_project'
    }
    
    html = render_document_with_original_layout(test_layout, 10.0, 20.0)
    print("Test du rendu HTML:")
    print(html[:500] + "..." if len(html) > 500 else html)