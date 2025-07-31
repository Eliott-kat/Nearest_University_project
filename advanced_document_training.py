#!/usr/bin/env python3
"""
Entraînement avancé pour améliorer la reproduction exacte des documents
"""

import os
import logging
from typing import Dict, List
from document_layout_processor import layout_processor
from document_layout_renderer import layout_renderer

class AdvancedDocumentTraining:
    """Entraîne le système pour reproduire parfaitement les documents originaux"""
    
    def __init__(self):
        self.training_patterns = {
            'graduation_project': {
                'title_page_patterns': [
                    'NEAR EAST UNIVERSITY',
                    'FACULTY OF ENGINEERING',
                    'DEPARTMENT OF SOFTWARE ENGINEERING',
                    'GRADUATION PROJECT',
                    'Prepared by:',
                    'Student Number:',
                    'Supervisor:'
                ],
                'structure_order': [
                    'title_page', 'acknowledgements', 'abstract', 
                    'table_of_contents', 'introduction', 'chapters', 
                    'conclusion', 'references'
                ],
                'chapter_pattern': r'^CHAPTER\s+\d+',
                'section_pattern': r'^\d+\.\s+[A-Z]',
                'default_font': 'Times New Roman',
                'default_size': 12,
                'line_spacing': 1.5
            },
            'thesis': {
                'title_page_patterns': [
                    'THESIS',
                    'SUBMITTED TO',
                    'IN PARTIAL FULFILLMENT',
                    'MASTER OF',
                    'DOCTOR OF'
                ],
                'structure_order': [
                    'title_page', 'abstract', 'dedication', 
                    'acknowledgements', 'table_of_contents', 
                    'chapters', 'bibliography'
                ],
                'default_font': 'Times New Roman',
                'default_size': 12,
                'line_spacing': 2.0
            }
        }
    
    def train_document_recognition(self, file_path: str, text_content: str) -> Dict:
        """Entraîne la reconnaissance du type de document et améliore le formatage"""
        try:
            # Détecter le type de document avec précision
            doc_type = self._detect_document_type_advanced(text_content)
            
            # Appliquer les patterns spécifiques
            training_config = self.training_patterns.get(doc_type, self.training_patterns['graduation_project'])
            
            # Traiter avec configuration avancée
            layout_data = layout_processor.process_document_with_layout(file_path, text_content)
            
            # Améliorer la structure détectée
            enhanced_layout = self._enhance_layout_structure(layout_data, training_config)
            
            # Ajouter les métadonnées d'entraînement
            enhanced_layout['training_applied'] = True
            enhanced_layout['document_type_detected'] = doc_type
            enhanced_layout['training_config'] = training_config
            
            logging.info(f"🎓 Entraînement avancé appliqué: {doc_type}")
            
            return enhanced_layout
            
        except Exception as e:
            logging.error(f"Erreur entraînement avancé: {e}")
            return layout_processor.process_document_with_layout(file_path, text_content)
    
    def _detect_document_type_advanced(self, text: str) -> str:
        """Détection avancée du type de document"""
        text_upper = text.upper()
        
        # Graduation Project
        if any(pattern in text_upper for pattern in self.training_patterns['graduation_project']['title_page_patterns']):
            return 'graduation_project'
        
        # Thesis
        if any(pattern in text_upper for pattern in self.training_patterns['thesis']['title_page_patterns']):
            return 'thesis'
        
        # Report générique
        if 'REPORT' in text_upper:
            return 'report'
        
        # Par défaut
        return 'graduation_project'
    
    def _enhance_layout_structure(self, layout_data: Dict, training_config: Dict) -> Dict:
        """Améliore la structure avec les patterns d'entraînement"""
        if not layout_data.get('pages'):
            return layout_data
        
        enhanced_pages = []
        
        for page in layout_data['pages']:
            enhanced_page = self._enhance_page_structure(page, training_config)
            enhanced_pages.append(enhanced_page)
        
        layout_data['pages'] = enhanced_pages
        layout_data['training_enhanced'] = True
        
        return layout_data
    
    def _enhance_page_structure(self, page: Dict, training_config: Dict) -> Dict:
        """Améliore la structure d'une page selon les patterns"""
        if not page.get('content'):
            return page
        
        enhanced_content = []
        
        for content_item in page['content']:
            enhanced_item = self._enhance_content_item(content_item, training_config)
            enhanced_content.append(enhanced_item)
        
        page['content'] = enhanced_content
        page['enhanced'] = True
        
        return page
    
    def _enhance_content_item(self, content_item: Dict, training_config: Dict) -> Dict:
        """Améliore un élément de contenu selon les patterns"""
        text = content_item.get('content', '')
        content_type = content_item.get('type', 'paragraph')
        
        # Améliorer le style selon le type détecté
        enhanced_style = content_item.get('style', {}).copy()
        
        # Appliquer les styles par défaut si manquants
        if not enhanced_style.get('font_name'):
            enhanced_style['font_name'] = training_config['default_font']
        
        if not enhanced_style.get('font_size'):
            if content_type == 'title_page':
                enhanced_style['font_size'] = training_config['default_size'] + 4
            elif content_type == 'chapter_title':
                enhanced_style['font_size'] = training_config['default_size'] + 2
            elif content_type == 'section_title':
                enhanced_style['font_size'] = training_config['default_size'] + 1
            else:
                enhanced_style['font_size'] = training_config['default_size']
        
        if not enhanced_style.get('line_spacing'):
            enhanced_style['line_spacing'] = training_config['line_spacing']
        
        # Améliorer l'alignement
        if content_type == 'title_page' and not content_item.get('alignment'):
            content_item['alignment'] = 'center'
        elif content_type in ['chapter_title', 'special_section'] and not content_item.get('alignment'):
            content_item['alignment'] = 'center'
        
        content_item['style'] = enhanced_style
        content_item['training_enhanced'] = True
        
        return content_item
    
    def apply_professional_spacing(self, layout_data: Dict) -> Dict:
        """Applique un espacement professionnel académique"""
        if not layout_data.get('pages'):
            return layout_data
        
        for page in layout_data['pages']:
            if not page.get('content'):
                continue
            
            for i, content_item in enumerate(page['content']):
                style = content_item.get('style', {})
                content_type = content_item.get('type', 'paragraph')
                
                # Espacements académiques standards
                if content_type == 'title_page':
                    style['space_before'] = 24
                    style['space_after'] = 18
                elif content_type == 'chapter_title':
                    style['space_before'] = 36
                    style['space_after'] = 24
                elif content_type == 'section_title':
                    style['space_before'] = 18
                    style['space_after'] = 12
                elif content_type == 'paragraph':
                    style['space_before'] = 0
                    style['space_after'] = 6
                    style['first_line_indent'] = 36  # 0.5 inch
                
                content_item['style'] = style
        
        layout_data['professional_spacing_applied'] = True
        return layout_data

# Instance globale
advanced_trainer = AdvancedDocumentTraining()

def train_document_advanced(file_path: str, text_content: str) -> Dict:
    """Fonction utilitaire pour l'entraînement avancé"""
    return advanced_trainer.train_document_recognition(file_path, text_content)

if __name__ == "__main__":
    # Test de l'entraînement
    test_text = """
NEAR EAST UNIVERSITY
FACULTY OF ENGINEERING
DEPARTMENT OF SOFTWARE ENGINEERING

GRADUATION PROJECT

Brain Tumor Detector Using CNN

Prepared by: Mudaser Mussa
Student Number: 20214521
Supervisor: Dr. Example

ACKNOWLEDGEMENTS

I would like to thank my family and friends for their support.

CHAPTER 1
INTRODUCTION

This study demonstrates the application of deep learning.
"""
    
    result = train_document_advanced("test.docx", test_text)
    print("Test entraînement avancé:")
    print(f"Type détecté: {result.get('document_type_detected')}")
    print(f"Entraînement appliqué: {result.get('training_applied')}")