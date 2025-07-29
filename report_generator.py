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
        """Generate HTML report for document analysis"""
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
            
            # Generate highlighted text
            highlighted_text = self._generate_highlighted_text(
                document.extracted_text or "",
                plagiarism_sentences,
                ai_sentences
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
            html_content = self.generate_html_report(document)
            if not html_content:
                return None
            
            # Generate PDF filename
            pdf_filename = f"report_{document.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_path = os.path.join(self.reports_dir or 'uploads/reports', pdf_filename)
            
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
            html_doc = weasyprint.HTML(string=html_content)
            css_doc = weasyprint.CSS(string=css_string)
            
            # Generate PDF
            html_doc.write_pdf(pdf_path, stylesheets=[css_doc])
            
            logging.info(f"Successfully generated PDF report: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logging.error(f"Failed to generate PDF report for document {document.id}: {e}")
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

# Global report generator instance
report_generator = ReportGenerator()
