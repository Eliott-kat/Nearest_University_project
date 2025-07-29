import os
import logging
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file, abort
# from flask_login import current_user  # Commented out for local installation
from werkzeug.exceptions import RequestEntityTooLarge
from app import app, db
from models import Document, AnalysisResult, HighlightedSentence, DocumentStatus, UserRole
# Commented out for local installation - uncomment if using auth system
# from auth_system import require_login, make_auth_blueprint
from file_utils import save_uploaded_file, extract_text_from_file, get_file_size
from copyleaks_service import copyleaks_service
from report_generator import report_generator

# Register authentication blueprint - commented out for local installation
# app.register_blueprint(make_auth_blueprint(), url_prefix="/auth")

# Simple local authentication replacement
def require_login(f):
    """Simple decorator for local development - bypasses authentication"""
    return f

# Create a fake user for local development
class FakeUser:
    def __init__(self):
        self.id = "local-user"
        self.email = "demo@acadcheck.local"
        self.first_name = "Demo"
        self.last_name = "User"
        self.role = UserRole.STUDENT
        self.is_authenticated = True

fake_user = FakeUser()

# Override current_user for local development
@app.before_request
def set_fake_user():
    from flask import g
    g.current_user = fake_user

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page or dashboard based on authentication status"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/dashboard')
@require_login
def dashboard():
    """User dashboard showing recent documents and statistics"""
    # Get user's recent documents
    recent_documents = Document.query.filter_by(user_id=current_user.id)\
                                   .order_by(Document.created_at.desc())\
                                   .limit(5)\
                                   .all()
    
    # Calculate statistics
    total_documents = Document.query.filter_by(user_id=current_user.id).count()
    completed_analyses = Document.query.filter_by(user_id=current_user.id, status=DocumentStatus.COMPLETED).count()
    processing_documents = Document.query.filter_by(user_id=current_user.id, status=DocumentStatus.PROCESSING).count()
    
    # Calculate average scores for completed analyses
    avg_plagiarism_score = 0
    avg_ai_score = 0
    
    completed_docs = Document.query.filter_by(user_id=current_user.id, status=DocumentStatus.COMPLETED).all()
    if completed_docs:
        plagiarism_scores = []
        ai_scores = []
        
        for doc in completed_docs:
            if doc.analysis_result:
                if doc.analysis_result.plagiarism_score is not None:
                    plagiarism_scores.append(doc.analysis_result.plagiarism_score)
                if doc.analysis_result.ai_score is not None:
                    ai_scores.append(doc.analysis_result.ai_score)
        
        if plagiarism_scores:
            avg_plagiarism_score = sum(plagiarism_scores) / len(plagiarism_scores)
        if ai_scores:
            avg_ai_score = sum(ai_scores) / len(ai_scores)
    
    stats = {
        'total_documents': total_documents,
        'completed_analyses': completed_analyses,
        'processing_documents': processing_documents,
        'avg_plagiarism_score': avg_plagiarism_score,
        'avg_ai_score': avg_ai_score
    }
    
    return render_template('dashboard.html', 
                         recent_documents=recent_documents, 
                         stats=stats,
                         user=current_user)

@app.route('/upload', methods=['GET', 'POST'])
@require_login
def upload_document():
    """Upload and submit document for analysis"""
    if request.method == 'POST':
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                flash('No file selected', 'danger')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected', 'danger')
                return redirect(request.url)
            
            # Save uploaded file
            file_info = save_uploaded_file(file)
            if not file_info:
                flash('Invalid file type. Please upload PDF, DOCX, or TXT files only.', 'danger')
                return redirect(request.url)
            
            file_path, filename = file_info
            
            # Extract text content
            content_type = file.content_type or 'text/plain'
            extracted_text = extract_text_from_file(file_path, content_type)
            if not extracted_text:
                flash('Could not extract text from the uploaded file.', 'danger')
                return redirect(request.url)
            
            # Create document record
            document = Document()
            document.filename = filename
            document.original_filename = file.filename
            document.file_path = file_path
            document.file_size = get_file_size(file_path)
            document.content_type = content_type
            document.extracted_text = extracted_text
            document.user_id = current_user.id
            document.status = DocumentStatus.UPLOADED
            
            db.session.add(document)
            db.session.commit()
            
            # Submit to Copyleaks for analysis
            if copyleaks_service.submit_document(document):
                flash('Document uploaded successfully and submitted for analysis!', 'success')
                return redirect(url_for('document_history'))
            else:
                flash('Document uploaded but failed to submit for analysis. Please try again.', 'warning')
                return redirect(url_for('document_history'))
            
        except RequestEntityTooLarge:
            flash('File too large. Maximum file size is 16MB.', 'danger')
            return redirect(request.url)
        except Exception as e:
            logging.error(f"Error uploading document: {e}")
            flash('An error occurred while uploading the document.', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html', user=current_user)

@app.route('/history')
@require_login
def document_history():
    """View document submission history"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Query user's documents with pagination
    documents = Document.query.filter_by(user_id=current_user.id)\
                             .order_by(Document.created_at.desc())\
                             .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('history.html', 
                         documents=documents,
                         user=current_user)

@app.route('/report/<int:document_id>')
@require_login
def view_report(document_id):
    """View detailed analysis report"""
    document = Document.query.get_or_404(document_id)
    
    # Check if user owns the document or is admin/professor
    if document.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.PROFESSOR]:
        abort(403)
    
    if document.status != DocumentStatus.COMPLETED:
        flash('Analysis is not yet complete for this document.', 'info')
        return redirect(url_for('document_history'))
    
    analysis_result = document.analysis_result
    if not analysis_result:
        flash('No analysis results found for this document.', 'danger')
        return redirect(url_for('document_history'))
    
    # Get highlighted sentences
    plagiarism_sentences = HighlightedSentence.query.filter_by(
        document_id=document.id,
        is_plagiarism=True
    ).all()
    
    ai_sentences = HighlightedSentence.query.filter_by(
        document_id=document.id,
        is_ai_generated=True
    ).all()
    
    # Generate highlighted text for display
    highlighted_text = report_generator._generate_highlighted_text(
        document.extracted_text or "",
        plagiarism_sentences,
        ai_sentences
    )
    
    return render_template('report.html',
                         document=document,
                         analysis_result=analysis_result,
                         highlighted_text=highlighted_text,
                         plagiarism_sentences=plagiarism_sentences,
                         ai_sentences=ai_sentences,
                         user=current_user)

@app.route('/download_report/<int:document_id>')
@require_login
def download_report(document_id):
    """Download PDF report"""
    document = Document.query.get_or_404(document_id)
    
    # Check if user owns the document or is admin/professor
    if document.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.PROFESSOR]:
        abort(403)
    
    if document.status != DocumentStatus.COMPLETED:
        flash('Analysis is not yet complete for this document.', 'info')
        return redirect(url_for('document_history'))
    
    # Generate PDF report
    pdf_path = report_generator.generate_pdf_report(document)
    if not pdf_path:
        flash('Failed to generate PDF report.', 'danger')
        return redirect(url_for('view_report', document_id=document_id))
    
    # Send file for download
    return send_file(pdf_path, 
                     as_attachment=True,
                     download_name=f"acadcheck_report_{document.original_filename}.pdf",
                     mimetype='application/pdf')

@app.route('/webhook/<status>/<scan_id>', methods=['POST'])
def webhook_handler(status, scan_id):
    """Handle webhook from Copyleaks API"""
    try:
        result_data = request.get_json() or {}
        
        logging.info(f"Received webhook for scan_id {scan_id} with status {status}")
        
        # Process the webhook result
        success = copyleaks_service.process_webhook_result(scan_id, status, result_data)
        
        if success:
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error'}), 400
            
    except Exception as e:
        logging.error(f"Error processing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin')
@require_login
def admin_dashboard():
    """Admin dashboard for managing all documents and users"""
    if current_user.role != UserRole.ADMIN:
        abort(403)
    
    # Get all documents
    all_documents = Document.query.order_by(Document.created_at.desc()).limit(20).all()
    
    # Get statistics
    total_users = db.session.query(db.func.count(db.distinct(Document.user_id))).scalar()
    total_documents = Document.query.count()
    completed_analyses = Document.query.filter_by(status=DocumentStatus.COMPLETED).count()
    
    stats = {
        'total_users': total_users,
        'total_documents': total_documents,
        'completed_analyses': completed_analyses
    }
    
    return render_template('admin_dashboard.html',
                         documents=all_documents,
                         stats=stats,
                         user=current_user)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash('File too large. Maximum file size is 16MB.', 'danger')
    return redirect(url_for('upload_document'))
