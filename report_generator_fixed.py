import os
import tempfile
import logging
from typing import Optional
from datetime import datetime
from flask import render_template, current_app
import weasyprint
from models import Document, AnalysisResult, HighlightedSentence

class ReportGenerator:
    def __init__(self):
        self.reports_dir = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of reports directory"""
        if not self._initialized:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            self.reports_dir = os.path.join(upload_folder, 'reports')
            os.makedirs(self.reports_dir, exist_ok=True)
            self._initialized = True
    
    def generate_html_report(self, document: Document) -> Optional[str]:
        """Generate HTML report for document analysis with original layout and real highlighting"""
        self._ensure_initialized()
        try:
            analysis_result = document.analysis_result
            if not analysis_result:
                logging.error(f"No analysis result found for document {document.id}")
                return None

            # Get highlighted sentences
            plagiarism_sentences = HighlightedSentence.query.filter_by(
                document_id=document.id,
                is_plagiarism=True
            ).all()
            ai_sentences = HighlightedSentence.query.filter_by(
                document_id=document.id,
                is_ai_generated=True
            ).all()

            # Rendu fidèle du document avec mise en page originale exacte
            from document_layout_renderer import render_document_with_original_layout
            import os
            
            # Créer une structure de mise en page basée sur le document original
            layout_data = self._create_document_layout(document, analysis_result)
            
            # Utiliser le rendu de mise en page avancé
            highlighted_text = render_document_with_original_layout(
                layout_data,
                float(getattr(analysis_result, 'plagiarism_score', 0)),
                float(getattr(analysis_result, 'ai_score', 0))
            )

            # Prepare report data
            report_data = {
                'document': document,
                'analysis_result': analysis_result,
                'highlighted_text': highlighted_text,
                'plagiarism_sentences': plagiarism_sentences,
                'ai_sentences': ai_sentences,
                'generated_at': datetime.now(),
                'total_issues': len(plagiarism_sentences) + len(ai_sentences)
            }

            # Render HTML template
            html_content = render_template('report_pdf.html', **report_data)
            return html_content

        except Exception as e:
            logging.error(f"Failed to generate HTML report for document {document.id}: {e}")
            return None
    
    def generate_pdf_report(self, document: Document) -> Optional[str]:
        """Generate PDF report for document analysis"""
        self._ensure_initialized()
        try:
            logging.info(f"Starting PDF generation for document {document.id}")
            
            html_content = self.generate_html_report(document)
            if not html_content:
                logging.error(f"No HTML content generated for document {document.id}")
                return None
            
            # Generate PDF filename
            pdf_filename = f"report_{document.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.reports_dir or 'uploads/reports', pdf_filename)
            
            logging.info(f"PDF path: {pdf_path}")
            
            # Generate PDF using WeasyPrint
            css_string = """
                @page {
                    margin: 2cm;
                    @top-center {
                        content: "AcadCheck - Academic Integrity Report";
                        font-size: 12pt;
                        font-weight: bold;
                    }
                    @bottom-center {
                        content: "Page " counter(page) " of " counter(pages);
                        font-size: 10pt;
                    }
                }
                
                body {
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                }
                
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
                
                .highlight-both {
                    background-color: #fff3e0;
                    border-left: 4px solid #ff9800;
                    padding: 2px 4px;
                    margin: 1px 0;
                }
                
                .score-high { color: #d32f2f; font-weight: bold; }
                .score-medium { color: #f57c00; font-weight: bold; }
                .score-low { color: #388e3c; font-weight: bold; }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }
                
                th, td {
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }
                
                th {
                    background-color: #f5f5f5;
                    font-weight: bold;
                }
            """
            
            # Create WeasyPrint HTML document
            try:
                html_doc = weasyprint.HTML(string=html_content)
                css_doc = weasyprint.CSS(string=css_string)
                
                # Generate PDF
                html_doc.write_pdf(pdf_path, stylesheets=[css_doc])
                
                # Verify PDF was created
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                    logging.info(f"✅ Successfully generated PDF report: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
                    return pdf_path
                else:
                    logging.error(f"❌ PDF file was not created or is empty: {pdf_path}")
                    return None
                    
            except Exception as weasyprint_error:
                logging.error(f"WeasyPrint error: {weasyprint_error}")
                # Fallback: try without CSS
                try:
                    html_doc.write_pdf(pdf_path)
                    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                        logging.info(f"✅ PDF generated without CSS: {pdf_path}")
                        return pdf_path
                    else:
                        logging.error("❌ PDF generation failed even without CSS")
                        return None
                except Exception as fallback_error:
                    logging.error(f"Fallback PDF generation failed: {fallback_error}")
                    return None
            
        except Exception as e:
            logging.error(f"❌ Failed to generate PDF report for document {document.id}: {e}")
            logging.error(f"Error type: {type(e).__name__}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _generate_highlighted_text(self, original_text: str, plagiarism_sentences: list, ai_sentences: list) -> str:
        """Generate HTML text with highlighted problematic sentences"""
        if not original_text:
            return ""
        
        try:
            # Create a list of all highlights with their positions
            highlights = []
            
            # Add plagiarism highlights
            for sentence in plagiarism_sentences:
                highlights.append({
                    'start': sentence.start_position,
                    'end': sentence.end_position,
                    'type': 'plagiarism',
                    'text': sentence.sentence_text,
                    'confidence': sentence.plagiarism_confidence,
                    'source_url': sentence.source_url,
                    'source_title': sentence.source_title
                })
            
            # Add AI highlights
            for sentence in ai_sentences:
                highlights.append({
                    'start': sentence.start_position,
                    'end': sentence.end_position,
                    'type': 'ai',
                    'text': sentence.sentence_text,
                    'confidence': sentence.ai_confidence,
                    'source_url': None,
                    'source_title': 'Contenu IA détecté'
                })
            
            # Sort highlights by start position
            highlights.sort(key=lambda x: x['start'])
            
            # Build highlighted text
            result = ""
            last_pos = 0
            
            for highlight in highlights:
                start_pos = max(0, highlight['start'])
                end_pos = min(len(original_text), highlight['end'])
                
                # Add text before highlight
                if start_pos > last_pos:
                    result += original_text[last_pos:start_pos]
                
                # Add highlighted text
                highlighted_text = original_text[start_pos:end_pos]
                css_class = f"highlight-{highlight['type']}"
                
                # Créer un tooltip informatif
                tooltip = f"{highlight['type'].title()}: {highlight['confidence']:.1f}% confidence"
                if highlight.get('source_url') and highlight['type'] == 'plagiarism':
                    tooltip += f" - Source: {highlight.get('source_title', 'Document externe')}"
                
                result += f'<span class="{css_class}" title="{tooltip}" style="cursor: help; position: relative;">{highlighted_text}</span>'
                
                last_pos = end_pos
            
            # Add remaining text
            if last_pos < len(original_text):
                result += original_text[last_pos:]
            
            return result
            
        except Exception as e:
            logging.error(f"Failed to generate highlighted text: {e}")
            return original_text
    
    def get_score_class(self, score: float) -> str:
        """Get CSS class for score display"""
        if score >= 30:
            return "score-high"
        elif score >= 15:
            return "score-medium"
        else:
            return "score-low"
    
    def _create_document_layout(self, document: Document, analysis_result: AnalysisResult) -> dict:
        """Create document layout structure based on original document"""
        try:
            # Extraire le texte et analyser la structure
            text = document.extracted_text or ""
            
            # Diviser en paragraphes pour simuler la structure du document
            paragraphs = text.split('\n\n')
            
            # Créer une structure de mise en page basique mais fidèle
            pages = []
            current_page = {
                'type': 'content',
                'content': []
            }
            
            # Ajouter chaque paragraphe avec son style original présumé
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    # Déterminer le type de contenu basé sur la position et le contenu
                    content_type = 'paragraph'
                    if i == 0 and len(paragraph) < 200:
                        content_type = 'title_page'  # Premier paragraphe court = titre
                    elif paragraph.strip().isupper() and len(paragraph) < 100:
                        content_type = 'chapter_title'  # Texte en majuscules = titre de chapitre
                    
                    # Style basé sur la position dans le document
                    style = {
                        'font_size': 12 if content_type == 'paragraph' else 16,
                        'bold': content_type != 'paragraph',
                        'alignment': 'center' if content_type != 'paragraph' else 'justify'
                    }
                    
                    current_page['content'].append({
                        'type': content_type,
                        'content': paragraph,
                        'style': style,
                        'alignment': 'center' if content_type != 'paragraph' else 'justify'
                    })
            
            pages.append(current_page)
            
            return {
                'type': 'document_with_layout',
                'pages': pages,
                'total_pages': len(pages),
                'document_type': document.original_filename.split('.')[-1].upper() if hasattr(document, 'original_filename') else 'DOCUMENT'
            }
            
        except Exception as e:
            logging.error(f"Error creating document layout: {e}")
            # Fallback: simple document structure
            return {
                'type': 'simple_document',
                'pages': [{
                    'type': 'content',
                    'content': [{
                        'type': 'paragraph',
                        'content': document.extracted_text or "",
                        'style': {'font_size': 12},
                        'alignment': 'justify'
                    }]
                }],
                'total_pages': 1,
                'document_type': 'SIMPLE'
            }

# Global report generator instance
report_generator = ReportGenerator()
