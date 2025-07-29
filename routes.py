"""
Simplified routes for local installation without authentication
"""
import os
import logging
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file, abort
from language_utils import LanguageManager
from werkzeug.exceptions import RequestEntityTooLarge
from app import app, db
from models import Document, AnalysisResult, HighlightedSentence, DocumentStatus, UserRole
from file_utils import save_uploaded_file, extract_text_from_file, get_file_size
from unified_detection_service import UnifiedDetectionService
from detection_status_display import get_provider_display_name, get_provider_status_badge
from report_generator import report_generator

# Create a fake user for local development
class FakeUser:
    def __init__(self):
        self.id = "local-user"
        self.email = "user@acadcheck.local"
        self.first_name = "Student"
        self.last_name = ""
        self.role = UserRole.STUDENT
        self.is_authenticated = True
        self.profile_image_url = None

fake_user = FakeUser()

# Make session permanent and inject current_user for templates
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.context_processor
def inject_user():
    """Inject current_user and user into all templates"""
    return dict(current_user=fake_user, user=fake_user)

@app.route('/')
def index():
    """Main landing page - shows dashboard directly for local version"""
    return dashboard()

@app.route('/dashboard')
def dashboard():
    """User dashboard with document statistics"""
    try:
        recent_documents = Document.query.filter_by(user_id=fake_user.id)\
            .order_by(Document.created_at.desc())\
            .limit(5).all()
        
        # Calculate statistics
        total_documents = Document.query.filter_by(user_id=fake_user.id).count()
        completed_analyses = Document.query.filter_by(
            user_id=fake_user.id, 
            status=DocumentStatus.COMPLETED
        ).count()
        processing_documents = Document.query.filter_by(
            user_id=fake_user.id,
            status=DocumentStatus.PROCESSING
        ).count()
        
        # Calculate average scores
        completed_docs = Document.query.filter_by(
            user_id=fake_user.id,
            status=DocumentStatus.COMPLETED
        ).all()
        
        if completed_docs:
            avg_plagiarism_score = sum(
                doc.analysis_result.plagiarism_score for doc in completed_docs 
                if doc.analysis_result
            ) / len([doc for doc in completed_docs if doc.analysis_result])
            avg_ai_score = sum(
                doc.analysis_result.ai_score for doc in completed_docs 
                if doc.analysis_result
            ) / len([doc for doc in completed_docs if doc.analysis_result])
        else:
            avg_plagiarism_score = 0
            avg_ai_score = 0
    
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        recent_documents = []
        avg_plagiarism_score = 0
        avg_ai_score = 0
        total_documents = 0
        completed_analyses = 0
        processing_documents = 0
    
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
                         user=fake_user)

@app.route('/upload', methods=['GET', 'POST'])
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
            document.user_id = fake_user.id
            document.status = DocumentStatus.UPLOADED
            
            db.session.add(document)
            db.session.commit()
            
            try:
                # Submit to unified detection service (3-tier system)
                unified_service = UnifiedDetectionService()
                result = unified_service.analyze_text(extracted_text, filename)
                
                if result and 'plagiarism' in result:
                    # Save analysis results
                    analysis_result = AnalysisResult()
                    analysis_result.document_id = document.id
                    analysis_result.plagiarism_score = result['plagiarism']['percent']
                    # Utiliser le score IA réel de l'algorithme local
                    # Utiliser le score IA réel de l'algorithme local avec vérification
                    ai_content = result.get('ai_content', {})
                    if isinstance(ai_content, dict):
                        analysis_result.ai_score = ai_content.get('percent', 0)
                    else:
                        analysis_result.ai_score = 0
                    analysis_result.sources_count = result['plagiarism']['sources_found']
                    analysis_result.analysis_provider = result.get('provider_used', 'unknown')
                    analysis_result.raw_response = str(result)
                    
                    db.session.add(analysis_result)
                    document.status = DocumentStatus.COMPLETED
                    db.session.commit()
                    
                    provider_name = get_provider_display_name(result.get('provider_used', 'local'))
                    score = result["plagiarism"]["percent"]
                    flash(f'✅ Document analysé avec succès! Plagiat détecté: {score}% via {provider_name}', 'success')
                    return redirect(url_for('document_history'))
                else:
                    flash('Document uploaded but analysis failed. Please try again.', 'warning')
                    return redirect(url_for('document_history'))
            except Exception as analysis_error:
                logging.error(f"Erreur lors de l'analyse: {analysis_error}")
                # Rollback en cas d'erreur
                db.session.rollback()
                flash('Une erreur est survenue lors de l\'analyse. Veuillez réessayer.', 'danger')
                return redirect(url_for('document_history'))
            
        except RequestEntityTooLarge:
            flash('File too large. Maximum file size is 16MB.', 'danger')
            return redirect(request.url)
        except Exception as e:
            logging.error(f"Error uploading document: {e}")
            flash('An error occurred while uploading the document.', 'danger')
            return redirect(request.url)
    
    return render_template('upload.html', user=fake_user)

@app.route('/history')
def document_history():
    """View document submission history"""
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of documents per page
    
    try:
        documents = Document.query.filter_by(user_id=fake_user.id)\
            .order_by(Document.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
            
        return render_template('history.html', 
                             documents=documents,
                             user=fake_user)
    except Exception as e:
        logging.error(f"Error loading document history: {e}")
        flash('Error loading document history.', 'danger')
        return render_template('history.html', 
                             documents=None,
                             user=fake_user)

@app.route('/report/<int:document_id>')
def view_report(document_id):
    """View detailed analysis report"""
    try:
        document = Document.query.filter_by(
            id=document_id, 
            user_id=fake_user.id
        ).first_or_404()
        
        if document.status != DocumentStatus.COMPLETED:
            flash('Analysis not yet completed for this document.', 'warning')
            return redirect(url_for('document_history'))
        
        # Get analysis results
        analysis_result = AnalysisResult.query.filter_by(document_id=document.id).first()
        if not analysis_result:
            flash('No analysis results found for this document.', 'warning')
            return redirect(url_for('document_history'))
        
        # Get highlighted sentences
        plagiarism_sentences = HighlightedSentence.query.filter_by(
            document_id=document.id,
            is_plagiarism=True
        ).order_by(HighlightedSentence.start_position).all()
        
        ai_sentences = HighlightedSentence.query.filter_by(
            document_id=document.id,
            is_ai_generated=True
        ).order_by(HighlightedSentence.start_position).all()
        
        # Generate highlighted text using report generator
        from report_generator import report_generator
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
                             user=fake_user)
                             
    except Exception as e:
        logging.error(f"Error loading report for document {document_id}: {e}")
        flash('Error loading report.', 'danger')
        return redirect(url_for('document_history'))

@app.route('/download-report/<int:document_id>')
def download_report(document_id):
    """Download PDF report"""
    try:
        document = Document.query.filter_by(
            id=document_id, 
            user_id=fake_user.id
        ).first_or_404()
        
        if document.status != DocumentStatus.COMPLETED:
            flash('Analysis not yet completed for this document.', 'warning')
            return redirect(url_for('document_history'))
        
        # Generate PDF report
        pdf_path = report_generator.generate_pdf_report(document)
        if not pdf_path or not os.path.exists(pdf_path):
            flash('Error generating PDF report.', 'danger')
            return redirect(url_for('view_report', document_id=document_id))
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"analysis_report_{document.original_filename}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"Error downloading report for document {document_id}: {e}")
        flash('Error downloading report.', 'danger')
        return redirect(url_for('document_history'))

@app.route('/admin')
def admin_dashboard():
    """Administration dashboard with API service management"""
    try:
        # Get provider status from unified service
        unified_service = UnifiedDetectionService()
        service_status = unified_service.get_service_status()
        
        service_details = {
            'copyleaks': {
                'name': 'Copyleaks (Priorité 1)',
                'configured': service_status['copyleaks']['available'],
                'status': 'Configured' if service_status['copyleaks']['available'] else 'Not Configured',
                'description': service_status['copyleaks']['description']
            },
            'plagiarismcheck': {
                'name': 'PlagiarismCheck (Fallback)',
                'configured': service_status['plagiarismcheck']['available'],
                'status': 'Configured' if service_status['plagiarismcheck']['available'] else 'Not Configured',
                'description': service_status['plagiarismcheck']['description']
            },
            'turnitin_local': {
                'name': 'Algorithme Local (Final Fallback)',
                'configured': service_status['turnitin_local']['available'],
                'status': 'Always Available',
                'description': service_status['turnitin_local']['description']
            }
        }
        
        # Get statistics
        total_documents = Document.query.count()
        completed_analyses = Document.query.filter_by(status=DocumentStatus.COMPLETED).count()
        
        return render_template('admin_dashboard.html',
                             provider_status=service_status,
                             service_details=service_details,
                             total_documents=total_documents,
                             completed_analyses=completed_analyses,
                             user=fake_user)
                             
    except Exception as e:
        logging.error(f"Error loading admin dashboard: {e}")
        flash('Error loading admin dashboard.', 'danger')
        return redirect(url_for('index'))

@app.route('/admin/switch-provider', methods=['POST'])
def switch_provider():
    """Switch to a different API provider"""
    try:
        new_provider = request.form.get('provider')
        
        if new_provider not in ['copyleaks', 'plagiarismcheck']:
            flash('Invalid provider selected.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        # Le nouveau système unifié utilise automatiquement l'ordre de priorité
        # Copyleaks -> PlagiarismCheck -> Local Algorithm
        flash(f'Le système utilise maintenant automatiquement la priorité: Copyleaks → PlagiarismCheck → Algorithme Local', 'info')
        logging.info(f"Unified detection system manages priority automatically")
        
    except Exception as e:
        logging.error(f"Error switching provider: {e}")
        flash('Error switching provider.', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/test-provider/<provider>')
def test_provider(provider):
    """Test a specific provider authentication"""
    try:
        switch = simple_api_switch.get_active_service()
        
        if provider == 'copyleaks':
            service = switch.copyleaks_service
        elif provider == 'plagiarismcheck':
            service = switch.plagiarismcheck_service
        else:
            flash('Invalid provider specified.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        # Test authentication
        if service.authenticate():
            flash(f'{provider} authentication successful!', 'success')
        else:
            flash(f'{provider} authentication failed.', 'warning')
            
    except Exception as e:
        logging.error(f"Error testing provider {provider}: {e}")
        flash(f'Error testing {provider} provider.', 'danger')
    
    return redirect(url_for('admin_dashboard'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large. Maximum file size is 16MB.', 'danger')
    return redirect(url_for('upload_document'))

@app.route('/logout')
def logout():
    """Route de déconnexion simplifiée pour installation locale"""
    return redirect(url_for('index'))

@app.route('/login')  
def login():
    """Route de connexion simplifiée pour installation locale"""
    return redirect(url_for('index'))

# Route de changement de langue gérée par language_utils.py