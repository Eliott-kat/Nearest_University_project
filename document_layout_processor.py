#!/usr/bin/env python3
"""
Processeur de mise en page pour afficher les documents exactement comme dans l'original
"""

import re
import logging
from typing import Dict, List, Tuple
import docx
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

class DocumentLayoutProcessor:
    """Traite et préserve la mise en page originale des documents"""
    
    def __init__(self):
        self.page_breaks = [
            'ACKNOWLEDGEMENTS', 'ABSTRACT', 'TABLE OF CONTENTS', 
            'LIST OF FIGURES', 'LIST OF TABLES', 'CHAPTER', 'REFERENCES',
            'APPENDIX', 'BIBLIOGRAPHY'
        ]
        
        self.title_patterns = [
            r'^[A-Z][A-Z\s]{10,}$',  # Titres en majuscules
            r'^\s*CHAPTER\s+\d+',     # Chapitres
            r'^\s*\d+\.\s+[A-Z]',     # Sections numérotées
            r'^\s*\d+\.\d+\s+[A-Z]'   # Sous-sections
        ]
    
    def process_document_with_layout(self, file_path: str, text_content: str) -> Dict:
        """Traite un document en préservant sa mise en page originale"""
        try:
            if file_path.endswith('.docx'):
                return self._process_docx_layout(file_path, text_content)
            elif file_path.endswith('.pdf'):
                return self._process_pdf_layout(text_content)
            else:
                return self._process_text_layout(text_content)
        except Exception as e:
            logging.error(f"Erreur traitement mise en page: {e}")
            return self._fallback_layout(text_content)
    
    def _process_docx_layout(self, file_path: str, text_content: str) -> Dict:
        """Traite spécifiquement les fichiers DOCX avec mise en page"""
        try:
            doc = docx.Document(file_path)
            
            pages = []
            current_page = {'type': 'normal', 'content': [], 'style': {}}
            
            for para in doc.paragraphs:
                para_text = para.text.strip()
                if not para_text:
                    current_page['content'].append({'type': 'break', 'content': '<br>'})
                    continue
                
                # Détecter les sauts de page
                if self._is_page_break(para_text):
                    if current_page['content']:
                        pages.append(current_page)
                    current_page = {'type': 'section', 'content': [], 'style': {}}
                
                # Analyser le style du paragraphe
                style_info = self._extract_paragraph_style(para)
                
                # Détecter le type de contenu
                content_type = self._detect_content_type(para_text, style_info)
                
                current_page['content'].append({
                    'type': content_type,
                    'content': para_text,
                    'style': style_info,
                    'alignment': self._get_alignment(para)
                })
            
            # Ajouter la dernière page
            if current_page['content']:
                pages.append(current_page)
            
            return {
                'type': 'document_with_layout',
                'pages': pages,
                'total_pages': len(pages),
                'document_type': self._detect_document_type(text_content)
            }
            
        except Exception as e:
            logging.error(f"Erreur traitement DOCX: {e}")
            return self._fallback_layout(text_content)
    
    def _extract_paragraph_style(self, para) -> Dict:
        """Extrait les informations de style d'un paragraphe avec précision maximale"""
        style = {}
        
        try:
            if para.runs:
                first_run = para.runs[0]
                font = first_run.font
                
                # Taille de police exacte
                if font.size:
                    style['font_size'] = font.size.pt
                else:
                    # Détecter la taille selon le contenu
                    text = para.text.strip()
                    if any(word in text.upper() for word in ['UNIVERSITY', 'FACULTY', 'GRADUATION']):
                        style['font_size'] = 16
                    elif text.startswith('CHAPTER'):
                        style['font_size'] = 14
                    else:
                        style['font_size'] = 12
                
                # Police exacte
                style['font_name'] = font.name or 'Times New Roman'
                style['bold'] = font.bold or False
                style['italic'] = font.italic or False
                style['underline'] = font.underline or False
            
            # Alignement du paragraphe
            style['alignment'] = self._get_alignment(para)
            
            # Espacement exact
            if para.paragraph_format.space_before:
                style['space_before'] = para.paragraph_format.space_before.pt
            if para.paragraph_format.space_after:
                style['space_after'] = para.paragraph_format.space_after.pt
            
            # Indentation
            if para.paragraph_format.left_indent:
                style['left_indent'] = para.paragraph_format.left_indent.pt
            if para.paragraph_format.first_line_indent:
                style['first_line_indent'] = para.paragraph_format.first_line_indent.pt
            
            # Interligne
            if para.paragraph_format.line_spacing:
                style['line_spacing'] = para.paragraph_format.line_spacing
            
        except Exception as e:
            logging.error(f"Erreur extraction style: {e}")
        
        return style
    
    def _get_alignment(self, para) -> str:
        """Détermine l'alignement du paragraphe"""
        try:
            alignment = para.paragraph_format.alignment
            if alignment == WD_ALIGN_PARAGRAPH.CENTER:
                return 'center'
            elif alignment == WD_ALIGN_PARAGRAPH.RIGHT:
                return 'right'
            elif alignment == WD_ALIGN_PARAGRAPH.JUSTIFY:
                return 'justify'
            else:
                return 'left'
        except:
            return 'left'
    
    def _detect_content_type(self, text: str, style: Dict) -> str:
        """Détecte le type de contenu avec analyse avancée"""
        text_upper = text.upper()
        text_clean = text.strip()
        
        # Page de garde - détection avancée
        university_keywords = ['NEAR EAST UNIVERSITY', 'UNIVERSITY', 'FACULTY', 'DEPARTMENT', 'GRADUATION PROJECT']
        if any(keyword in text_upper for keyword in university_keywords):
            if (style.get('bold') or style.get('font_size', 0) >= 14 or 
                style.get('alignment') == 'center'):
                return 'title_page'
        
        # Informations étudiant sur page de garde
        if (any(keyword in text_upper for keyword in ['PREPARED BY', 'STUDENT NUMBER', 'SUPERVISOR']) or
            re.match(r'^\d{8}$', text_clean)):  # Numéro étudiant
            return 'title_page'
        
        # Titres de chapitres
        if (re.match(r'^CHAPTER\s+\d+', text_upper) or 
            (style.get('font_size', 0) >= 16 and style.get('bold'))):
            return 'chapter_title'
        
        # Sections spéciales
        special_sections = ['ACKNOWLEDGEMENTS', 'ABSTRACT', 'INTRODUCTION', 'CONCLUSION', 
                          'REFERENCES', 'BIBLIOGRAPHY', 'TABLE OF CONTENTS', 'LIST OF FIGURES']
        if text_upper in special_sections:
            return 'special_section'
        
        # Titres de sections numérotées
        if (re.match(r'^\d+\.?\s+[A-Z]', text) or 
            re.match(r'^\d+\.\d+\.?\s+[A-Z]', text) or
            (style.get('bold') and style.get('font_size', 0) >= 13)):
            return 'section_title'
        
        # Sous-titres
        if (re.match(r'^\d+\.\d+\.\d+\.?\s+[A-Z]', text) or
            (style.get('bold') and len(text_clean) < 80)):
            return 'sub_section'
        
        # Paragraphe normal
        return 'paragraph'
    
    def _is_page_break(self, text: str) -> bool:
        """Détermine si le texte indique un saut de page"""
        text_upper = text.upper()
        return any(keyword in text_upper for keyword in self.page_breaks)
    
    def _detect_document_type(self, text: str) -> str:
        """Détecte le type de document"""
        text_lower = text.lower()
        
        if 'graduation project' in text_lower:
            return 'graduation_project'
        elif 'thesis' in text_lower:
            return 'thesis'
        elif 'report' in text_lower:
            return 'report'
        else:
            return 'academic_document'
    
    def _process_pdf_layout(self, text_content: str) -> Dict:
        """Traite les PDF en tentant de préserver la mise en page"""
        # Pour les PDF, analyser le texte pour détecter la structure
        lines = text_content.split('\n')
        pages = []
        current_page = {'type': 'normal', 'content': [], 'style': {}}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            content_type = self._detect_content_type_from_text(line)
            
            if content_type in ['chapter_title', 'special_section']:
                if current_page['content']:
                    pages.append(current_page)
                current_page = {'type': 'section', 'content': [], 'style': {}}
            
            current_page['content'].append({
                'type': content_type,
                'content': line,
                'style': self._infer_style_from_text(line),
                'alignment': self._infer_alignment_from_text(line)
            })
        
        if current_page['content']:
            pages.append(current_page)
        
        return {
            'type': 'document_with_layout',
            'pages': pages,
            'total_pages': len(pages),
            'document_type': self._detect_document_type(text_content)
        }
    
    def _detect_content_type_from_text(self, text: str) -> str:
        """Détecte le type de contenu à partir du texte seul"""
        text_upper = text.upper()
        
        if re.match(r'^CHAPTER\s+\d+', text_upper):
            return 'chapter_title'
        elif text_upper in ['ACKNOWLEDGEMENTS', 'ABSTRACT', 'CONCLUSION', 'REFERENCES']:
            return 'special_section'
        elif re.match(r'^\d+\.\s+[A-Z]', text):
            return 'section_title'
        elif len(text) < 100 and text.isupper():
            return 'title_page'
        else:
            return 'paragraph'
    
    def _infer_style_from_text(self, text: str) -> Dict:
        """Infère le style à partir du texte"""
        style = {}
        
        if text.isupper() and len(text) < 100:
            style['bold'] = True
            style['font_size'] = 16
        elif re.match(r'^CHAPTER\s+\d+', text.upper()):
            style['bold'] = True
            style['font_size'] = 18
        elif re.match(r'^\d+\.\s+[A-Z]', text):
            style['bold'] = True
            style['font_size'] = 14
        else:
            style['font_size'] = 12
        
        return style
    
    def _infer_alignment_from_text(self, text: str) -> str:
        """Infère l'alignement à partir du texte"""
        if (text.isupper() and len(text) < 100) or 'UNIVERSITY' in text.upper():
            return 'center'
        else:
            return 'justify'
    
    def _process_text_layout(self, text_content: str) -> Dict:
        """Traite les fichiers texte simples"""
        return self._process_pdf_layout(text_content)
    
    def _fallback_layout(self, text_content: str) -> Dict:
        """Mise en page de base en cas d'erreur"""
        return {
            'type': 'simple_document',
            'pages': [{'type': 'normal', 'content': [
                {'type': 'paragraph', 'content': text_content, 'style': {}, 'alignment': 'justify'}
            ], 'style': {}}],
            'total_pages': 1,
            'document_type': 'document'
        }

# Instance globale
layout_processor = DocumentLayoutProcessor()

def process_document_layout(file_path: str, text_content: str) -> Dict:
    """Fonction utilitaire pour traiter la mise en page d'un document"""
    return layout_processor.process_document_with_layout(file_path, text_content)

if __name__ == "__main__":
    # Test du processeur
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

I would like to thank my family and friends for their support during this project.

ABSTRACT

This project presents a comprehensive analysis of brain tumor detection using convolutional neural networks.

CHAPTER 1
INTRODUCTION

This study demonstrates the application of deep learning techniques in medical imaging.
"""
    
    result = process_document_layout("test.docx", test_text)
    print("Test du processeur de mise en page:")
    print(f"Type: {result['type']}")
    print(f"Pages: {result['total_pages']}")
    print(f"Document type: {result['document_type']}")