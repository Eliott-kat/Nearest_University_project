"""
PDF Annotation Utility for AcadCheck
Uses PyMuPDF (fitz) to annotate PDF documents with highlights and underlines
for plagiarism and AI-generated content detection.
"""
import os
import re
import logging
import fitz  # PyMuPDF
from typing import List, Tuple, Optional, Dict, Any

# Colors for annotations
PLAGIARISM_COLOR = (1, 1, 0)  # Yellow highlight
AI_COLOR = (0, 0, 1)          # Blue underline

# Define a simple data structure for highlighted sentences
class HighlightedSentenceData:
    """Simple data structure for highlighted sentences without database dependencies"""
    def __init__(self, sentence_text: str, is_plagiarism: bool = False, 
                 is_ai_generated: bool = False, plagiarism_confidence: float = 0,
                 ai_confidence: float = 0):
        self.sentence_text = sentence_text
        self.is_plagiarism = is_plagiarism
        self.is_ai_generated = is_ai_generated
        self.plagiarism_confidence = plagiarism_confidence
        self.ai_confidence = ai_confidence

def normalize_text(text: str) -> str:
    """
    Normalize text for case-insensitive comparison and whitespace tolerance.
    """
    # Convert to lowercase and normalize whitespace
    text = text.lower().strip()
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text

def find_text_in_pdf(doc: fitz.Document, search_text: str, tolerance: float = 0.8) -> List[Tuple[int, fitz.Rect]]:
    """
    Find text in PDF with approximate matching and tolerance for whitespace variations.
    
    Args:
        doc: PyMuPDF document object
        search_text: Text to search for
        tolerance: Minimum similarity threshold (0.0 to 1.0)
    
    Returns:
        List of tuples (page_number, rectangle) where text was found
    """
    normalized_search = normalize_text(search_text)
    results = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_instances = page.search_for(search_text)
        
        # If exact match found, use it
        if text_instances:
            for rect in text_instances:
                results.append((page_num, rect))
            continue
        
        # If no exact match, try case-insensitive search
        page_text = page.get_text("text").lower()
        if normalized_search in page_text:
            # Get all text blocks and search for approximate matches
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            span_text = span["text"].lower()
                            if normalized_search in span_text:
                                # Calculate bounding box for this span
                                bbox = fitz.Rect(span["bbox"])
                                results.append((page_num, bbox))
    
    return results

def annotate_pdf_with_highlights(
    input_pdf_path: str, 
    output_pdf_path: str, 
    highlighted_sentences: List[HighlightedSentenceData]
) -> bool:
    """
    Annotate PDF with highlights for plagiarism and underlines for AI-generated content.
    
    Args:
        input_pdf_path: Path to original PDF file
        output_pdf_path: Path where annotated PDF will be saved
        highlighted_sentences: List of HighlightedSentence objects
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
        
        # Open the original PDF
        doc = fitz.open(input_pdf_path)
        
        # Process each highlighted sentence
        for sentence in highlighted_sentences:
            if not sentence.sentence_text:
                continue
                
            # Find the text in the PDF
            text_instances = find_text_in_pdf(doc, sentence.sentence_text)
            
            if not text_instances:
                logging.warning(f"Text not found in PDF: {sentence.sentence_text[:50]}...")
                continue
            
            # Annotate each found instance
            for page_num, rect in text_instances:
                page = doc.load_page(page_num)
                
                if sentence.is_plagiarism and sentence.plagiarism_confidence > 30:
                    # Add yellow highlight for plagiarism
                    annot = page.add_highlight_annot(rect)
                    annot.set_colors(stroke=PLAGIARISM_COLOR)
                    annot.update()
                
                if sentence.is_ai_generated and sentence.ai_confidence > 40:
                    # Add blue underline for AI content
                    # Create a rectangle at the bottom of the text for underline
                    underline_rect = fitz.Rect(rect.x0, rect.y1 - 2, rect.x1, rect.y1)
                    annot = page.add_rect_annot(underline_rect)
                    annot.set_colors(stroke=AI_COLOR)
                    annot.set_border(width=2)
                    annot.update()
        
        # Save the annotated PDF
        doc.save(output_pdf_path)
        doc.close()
        
        logging.info(f"Annotated PDF saved to: {output_pdf_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error annotating PDF: {e}")
        if 'doc' in locals():
            doc.close()
        return False

def generate_annotated_pdf_for_document(document_id: int, document_path: str) -> Optional[str]:
    """
    Generate an annotated PDF for a given document.
    
    Args:
        document_id: ID of the document in database
        document_path: Path to the original PDF file
    
    Returns:
        Path to the annotated PDF file, or None if failed
    """
    try:
        # Import database models only when needed to avoid circular imports
        from models import HighlightedSentence
        
        # Get highlighted sentences from database
        db_sentences = HighlightedSentence.query.filter_by(
            document_id=document_id
        ).all()
        
        if not db_sentences:
            logging.warning(f"No highlighted sentences found for document {document_id}")
            return None
        
        # Convert database objects to simple data structures
        highlighted_sentences = []
        for db_sentence in db_sentences:
            sentence_data = HighlightedSentenceData(
                sentence_text=db_sentence.sentence_text,
                is_plagiarism=db_sentence.is_plagiarism,
                is_ai_generated=db_sentence.is_ai_generated,
                plagiarism_confidence=db_sentence.plagiarism_confidence or 0,
                ai_confidence=db_sentence.ai_confidence or 0
            )
            highlighted_sentences.append(sentence_data)
        
        # Create output path for annotated PDF
        annotated_dir = os.path.join(os.path.dirname(document_path), "annotated_reports")
        filename = f"annotated_{os.path.basename(document_path)}"
        output_path = os.path.join(annotated_dir, filename)
        
        # Annotate the PDF
        success = annotate_pdf_with_highlights(
            document_path, output_path, highlighted_sentences
        )
        
        if success:
            return output_path
        else:
            return None
            
    except Exception as e:
        logging.error(f"Error generating annotated PDF for document {document_id}: {e}")
        return None
