"""
Document renderer that preserves original layout and formatting
with highlighting for plagiarism and AI detection
"""
import os
import logging
import tempfile
from typing import Optional
import mammoth
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import parse_xml
from docx.shared import RGBColor

def render_docx_with_original_layout_and_simple_highlighting(docx_path: str, 
                                                           extracted_text: str,
                                                           plagiarism_score: float,
                                                           ai_score: float) -> str:
    """
    Render DOCX document with original layout and simple highlighting
    """
    try:
        # Use mammoth to convert DOCX to HTML with basic styling
        with open(docx_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html_content = result.value
            
        # Add basic styling for highlights
        html_content = html_content.replace('</head>', '''
            <style>
                .highlight-plagiarism {
                    background-color: #ffebee;
                    border-left: 4px solid #f44336;
                    padding: 2px 4px;
                    margin: 1px 0;
                }
                .highlight-ai {
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 2px 4px;
                    margin: 1px 0;
                }
            </style>
            </head>
        ''')
        
        return html_content
        
    except Exception as e:
        logging.error(f"Error rendering DOCX with layout: {e}")
        # Fallback to simple text with highlighting
        return _generate_simple_highlighted_text(extracted_text, plagiarism_score, ai_score)

def render_pdf_with_original_layout_and_simple_highlighting(pdf_path: str,
                                                          extracted_text: str,
                                                          plagiarism_score: float,
                                                          ai_score: float) -> str:
    """
    Render PDF document with original layout information and simple highlighting
    """
    try:
        # Extract text with basic layout info from PDF
        reader = PdfReader(pdf_path)
        html_content = "<div style='font-family: Arial, sans-serif; line-height: 1.6;'>"
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text:
                html_content += f"<div style='page-break-before: always;'>"
                html_content += f"<h4 style='color: #666;'>Page {page_num}</h4>"
                html_content += f"<div style='border: 1px solid #eee; padding: 15px; margin: 10px 0;'>"
                html_content += f"<pre style='white-space: pre-wrap; font-family: inherit;'>{text}</pre>"
                html_content += "</div></div>"
        
        html_content += "</div>"
        
        # Add highlighting styles
        html_content = html_content.replace('</head>', '''
            <style>
                .highlight-plagiarism {
                    background-color: #ffebee;
                    border-left: 4px solid #f44336;
                    padding: 2px 4px;
                    margin: 1px 0;
                }
                .highlight-ai {
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 2px 4px;
                    margin: 1px 0;
                }
            </style>
            </head>
        ''')
        
        return html_content
        
    except Exception as e:
        logging.error(f"Error rendering PDF with layout: {e}")
        # Fallback to simple text with highlighting
        return _generate_simple_highlighted_text(extracted_text, plagiarism_score, ai_score)

def _generate_simple_highlighted_text(text: str, plagiarism_score: float, ai_score: float) -> str:
    """
    Generate simple highlighted text with layout simulation
    """
    if not text:
        return ""
    
    # Split into paragraphs to simulate document structure
    paragraphs = text.split('\n\n')
    highlighted_content = "<div style='font-family: Arial, sans-serif; line-height: 1.6; margin: 20px;'>"
    
    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():
            # Simulate paragraph with margin
            highlighted_content += f"<p style='margin-bottom: 12px; text-align: justify;'>"
            
            # Add simple highlighting based on scores (simulated)
            words = paragraph.split()
            total_words = len(words)
            
            # Calculate number of words to highlight
            plag_words = max(1, int(total_words * (plagiarism_score / 100)))
            ai_words = max(1, int(total_words * (ai_score / 100)))
            
            # Highlight words
            for j, word in enumerate(words):
                if j < plag_words:
                    highlighted_content += f"<span class='highlight-plagiarism'>{word}</span> "
                elif j < plag_words + ai_words:
                    highlighted_content += f"<span class='highlight-ai'>{word}</span> "
                else:
                    highlighted_content += f"{word} "
            
            highlighted_content += "</p>"
    
    highlighted_content += "</div>"
    
    return highlighted_content

def create_docx_with_highlights(original_docx_path: str, output_path: str, 
                               plagiarism_sentences: list, ai_sentences: list) -> bool:
    """
    Create a new DOCX file with original layout and highlighted problematic content
    """
    try:
        # Load original document
        doc = DocxDocument(original_docx_path)
        
        # Create highlighting styles
        _add_highlight_styles(doc)
        
        # Apply highlights to paragraphs
        _apply_highlights_to_docx(doc, plagiarism_sentences, ai_sentences)
        
        # Save the modified document
        doc.save(output_path)
        return True
        
    except Exception as e:
        logging.error(f"Error creating DOCX with highlights: {e}")
        return False

def _add_highlight_styles(doc):
    """Add custom highlighting styles to the document"""
    styles = doc.styles
    
    # Plagiarism highlight style
    if 'HighlightPlagiarism' not in styles:
        style = styles.add_style('HighlightPlagiarism', 1)
        style.font.color.rgb = RGBColor(255, 255, 255)
        style.font.bold = True
        paragraph_format = style.paragraph_format
        paragraph_format.left_indent = Inches(0.1)
        paragraph_format.right_indent = Inches(0.1)
        
        # Add shading
        shading_elm = parse_xml(r'<w:shd {} w:fill="FFEBEE"/>'.format(
            qn('w:val').format('clear')))
        style.element.rPr.append(shading_elm)
    
    # AI highlight style
    if 'HighlightAI' not in styles:
        style = styles.add_style('HighlightAI', 1)
        style.font.color.rgb = RGBColor(255, 255, 255)
        style.font.bold = True
        paragraph_format = style.paragraph_format
        paragraph_format.left_indent = Inches(0.1)
        paragraph_format.right_indent = Inches(0.1)
        
        # Add shading
        shading_elm = parse_xml(r'<w:shd {} w:fill="E3F2FD"/>'.format(
            qn('w:val').format('clear')))
        style.element.rPr.append(shading_elm)

def _apply_highlights_to_docx(doc, plagiarism_sentences, ai_sentences):
    """Apply highlights to DOCX paragraphs"""
    # This is a simplified implementation
    # In a real scenario, you'd need to match sentences with document content
    for paragraph in doc.paragraphs:
        text = paragraph.text
        if any(sentence.sentence_text in text for sentence in plagiarism_sentences):
            paragraph.style = doc.styles['HighlightPlagiarism']
        elif any(sentence.sentence_text in text for sentence in ai_sentences):
            paragraph.style = doc.styles['HighlightAI']
