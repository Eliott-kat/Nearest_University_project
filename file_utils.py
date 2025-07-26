import os
import uuid
import logging
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
import PyPDF2
import docx
from flask import current_app

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file) -> Optional[Tuple[str, str]]:
    """Save uploaded file and return (file_path, filename)"""
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        return None
    
    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Save file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        return file_path, unique_filename
        
    except Exception as e:
        logging.error(f"Failed to save uploaded file: {e}")
        return None

def extract_text_from_file(file_path: str, content_type: str) -> Optional[str]:
    """Extract text content from uploaded file"""
    try:
        if content_type == 'text/plain' or file_path.endswith('.txt'):
            return extract_text_from_txt(file_path)
        elif content_type == 'application/pdf' or file_path.endswith('.pdf'):
            return extract_text_from_pdf(file_path)
        elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file_path.endswith('.docx'):
            return extract_text_from_docx(file_path)
        else:
            logging.error(f"Unsupported file type: {content_type}")
            return None
            
    except Exception as e:
        logging.error(f"Failed to extract text from file {file_path}: {e}")
        return None

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        logging.error(f"Failed to extract text from PDF {file_path}: {e}")
        # Fallback: try with different encoding
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                text = content.decode('utf-8', errors='ignore')
        except:
            pass
    
    return text.strip()

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"Failed to extract text from DOCX {file_path}: {e}")
        return ""

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def delete_file(file_path: str) -> bool:
    """Delete file from filesystem"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        logging.error(f"Failed to delete file {file_path}: {e}")
        return False
