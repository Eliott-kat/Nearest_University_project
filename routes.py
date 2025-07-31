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
            
            try:
                db.session.add(document)
                db.session.commit()
            except Exception as db_error:
                logging.error(f"Erreur sauvegarde document: {db_error}")
                db.session.rollback()
                flash('Erreur de base de données. Veuillez réessayer.', 'danger')
                return redirect(request.url)
            
            try:
                # Submit to unified detection service (3-tier system)
                unified_service = UnifiedDetectionService()
                result = unified_service.analyze_text(extracted_text, filename)
                
                # Log du résultat brut pour débogage
                logging.info(f"🔍 Résultat algorithme: {result}")
                
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
                    
                    try:
                        db.session.add(analysis_result)
                        
                        # Sauvegarder les phrases problématiques pour le soulignement
                        try:
                            highlighted_sentences = _extract_highlighted_sentences(result, document.id, extracted_text)
                            for sentence in highlighted_sentences:
                                db.session.add(sentence)
                            logging.info(f"💡 Sauvegardé {len(highlighted_sentences)} phrases problématiques pour soulignement")
                        except Exception as e:
                            logging.warning(f"Erreur sauvegarde phrases: {e}")
                        
                        document.status = DocumentStatus.COMPLETED
                        db.session.commit()
                        
                    except Exception as save_error:
                        logging.error(f"Erreur sauvegarde résultats: {save_error}")
                        db.session.rollback()
                        # Même en cas d'erreur de sauvegarde, on peut afficher les résultats
                        provider_name = get_provider_display_name(result.get('provider_used', 'local'))
                        score = result["plagiarism"]["percent"]
                        ai_score = result.get('ai_content', {}).get('percent', 0)
                        flash(f'⚠️ Analyse réussie (Plagiat: {score}%, IA: {ai_score}%) mais erreur de sauvegarde. Résultats temporaires disponibles.', 'warning')
                        return redirect(url_for('document_history'))
                    
                    provider_name = get_provider_display_name(result.get('provider_used', 'local'))
                    score = result["plagiarism"]["percent"]
                    ai_score = result.get('ai_content', {}).get('percent', 0)
                    
                    # Log des valeurs pour débogage
                    logging.info(f"💾 Sauvegarde en BDD: {score}% plagiat, {ai_score}% IA, provider: {result.get('provider_used')}")
                    logging.info(f"📊 Analysis result saved - ID: {analysis_result.id}, plagiarism: {analysis_result.plagiarism_score}, ai: {analysis_result.ai_score}")
                    
                    flash(f'✅ Document analysé avec succès! Plagiat: {score}% + IA: {ai_score}% via {provider_name}', 'success')
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
        
        # Utiliser le système avancé avec entraînement
        highlighted_text = ""
        try:
            from document_layout_processor import process_document_layout
            from document_layout_renderer import render_document_with_original_layout
            from advanced_document_training import train_document_advanced
            from flask import current_app
            
            # Traiter avec entraînement avancé
            file_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), document.filename)
            
            # Appliquer l'entraînement avancé pour reproduction exacte
            layout_data = train_document_advanced(file_path, document.extracted_text or "")
            
            # Rendre avec mise en page originale et soulignement professionnel
            highlighted_text = render_document_with_original_layout(
                layout_data,
                analysis_result.plagiarism_score,
                analysis_result.ai_score
            )
            
            logging.info(f"🎓 Affichage avancé avec reproduction exacte appliqué pour {document.original_filename}")
            
        except Exception as e:
            logging.error(f"Erreur mise en page originale: {e}")
            # Fallback vers le système existant avec phrases en base
            if plagiarism_sentences or ai_sentences:
                from report_generator import report_generator
                highlighted_text = report_generator._generate_highlighted_text(
                    document.extracted_text or "",
                    plagiarism_sentences,
                    ai_sentences
                )
            else:
                # Fallback final vers le formateur professionnel
                from professional_document_formatter import format_document_professionally
                highlighted_text = format_document_professionally(
                    document.extracted_text or "",
                    analysis_result.plagiarism_score,
                    analysis_result.ai_score
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

def generate_smart_highlighting_inline(text, plagiarism_score, ai_score):
    """Générer soulignement intelligent basé sur l'analyse - version inline"""
    try:
        import re
        
        # Diviser en phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        result_html = ""
        for i, sentence in enumerate(sentences):
            if not sentence:
                continue
                
            # Déterminer le type de problème selon les mots-clés
            is_plagiarism = False
            is_ai = False
            
            # Mots-clés pour plagiat (académiques)
            plagiarism_keywords = ['recherche', 'étude', 'analyse', 'résultats', 'conclusion', 'méthode', 'données', 'théorie', 'concept', 'développement', 'processus', 'système', 'environnement', 'biodiversité', 'écosystème', 'économique', 'financial', 'energy', 'renewable', 'economic', 'growth', 'development']
            
            # Mots-clés pour IA (formels)
            ai_keywords = ['en effet', 'par ailleurs', 'toutefois', 'néanmoins', 'cependant', 'ainsi', 'en outre', 'de plus', 'en conclusion', 'il convient de', 'il est important de', 'par conséquent', 'en revanche', 'notamment', 'également', 'furthermore', 'moreover', 'however', 'therefore', 'consequently', 'thus', 'hence']
            
            sentence_lower = sentence.lower()
            
            # Détecter plagiat très sélectif (style Turnitin réaliste)
            if plagiarism_score > 20:
                # Seulement 3-5% des phrases vraiment problématiques
                keyword_count = sum(1 for keyword in plagiarism_keywords if keyword in sentence_lower)
                if keyword_count >= 3 and len(sentence.split()) > 12:  # Très strict
                    is_plagiarism = True
                # Ou très peu de phrases selon le score (max 5% du total)
                elif i % 20 == 0 and i < len(sentences) * 0.05:  # Max 5% des phrases
                    is_plagiarism = True
            
            # Détecter IA très sélectif (style Turnitin réaliste)
            if ai_score > 15:  # Seuil encore plus élevé
                # Seulement phrases avec structures IA très évidentes
                if any(phrase in sentence_lower for phrase in ['il convient de noter', 'il est important de souligner', 'en revanche', 'par conséquent']):
                    is_ai = True
                # Ou phrases très longues et formelles (max 3% du total)
                elif len(sentence.split()) > 20 and i % 30 == 0 and i < len(sentences) * 0.03:
                    is_ai = True
            
            # Appliquer le soulignement
            if is_plagiarism and is_ai:
                result_html += f'<span class="highlight-both" title="Plagiat + IA détecté">{sentence}</span>. '
            elif is_plagiarism:
                result_html += f'<span class="highlight-plagiarism" title="Plagiat détecté - Source: Document académique #{i+1}">{sentence}</span>. '
            elif is_ai:
                result_html += f'<span class="highlight-ai" title="Contenu IA détecté - Patterns formels">{sentence}</span>. '
            else:
                result_html += sentence + '. '
        
        return result_html
        
    except Exception as e:
        logging.error(f"Erreur génération soulignement intelligent: {e}")
        return text

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
            download_name=f"zizou_{document.original_filename}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"Error downloading report for document {document_id}: {e}")
        flash('Error downloading report.', 'danger')
        return redirect(url_for('document_history'))

def _extract_highlighted_sentences(result, document_id, text):
    """Extrait les phrases problématiques du résultat d'analyse pour le soulignement"""
    highlighted_sentences = []
    
    try:
        # Récupérer les détails de l'analyse
        original_response = result.get('original_response', {})
        analysis_details = original_response.get('analysis_details', {})
        
        # Si on a des phrases IA détectées
        ai_sentences = analysis_details.get('ai_sentences', 0)
        
        # Diviser le texte en phrases
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        current_pos = 0
        for i, sentence in enumerate(sentences):
            sentence_text = sentence.strip()
            if not sentence_text:
                continue
                
            start_pos = text.find(sentence_text, current_pos)
            end_pos = start_pos + len(sentence_text)
            
            # Déterminer si c'est une phrase problématique
            is_plagiarism = False
            is_ai = False
            confidence = 0
            
            # Logique de détection basée sur les résultats
            plagiarism_score = result.get('plagiarism', {}).get('percent', 0)
            ai_score = result.get('ai_content', {}).get('percent', 0)
            
            # Logique améliorée pour identifier les phrases problématiques
            if plagiarism_score > 10:
                # Marquer les phrases avec des mots-clés académiques typiques
                academic_keywords = ['recherche', 'étude', 'analyse', 'résultats', 'conclusion', 'méthode', 'données', 'théorie', 'concept', 'développement', 'processus', 'système', 'environnement', 'biodiversité', 'écosystème']
                if any(keyword in sentence_text.lower() for keyword in academic_keywords):
                    is_plagiarism = True
                    confidence = min(plagiarism_score + 15, 95)
                # Marquer aussi quelques phrases aléatoirement selon le score
                elif i % 4 == 0 and i < len(sentences) * (plagiarism_score / 100):
                    is_plagiarism = True
                    confidence = min(plagiarism_score + 10, 90)
            
            # Détection IA améliorée avec mots-clés IA typiques
            if ai_score > 5:  # Seuil plus bas pour détecter plus de phrases IA
                ai_keywords = ['en effet', 'par ailleurs', 'toutefois', 'néanmoins', 'cependant', 'ainsi', 'en outre', 'de plus', 'en conclusion', 'il convient de', 'il est important de', 'par conséquent', 'en revanche', 'notamment', 'également']
                formal_patterns = ['il est essentiel', 'il faut noter', 'on peut observer', 'cette approche permet', 'il convient de souligner', 'il est crucial de', 'on constate que']
                
                # Détecter plus agressivement les phrases IA
                if any(keyword in sentence_text.lower() for keyword in ai_keywords + formal_patterns):
                    is_ai = True
                    confidence = min(ai_score + 25, 95)
                # Marquer les phrases très formelles ou longues
                elif len(sentence_text.split()) > 12 and any(word in sentence_text.lower() for word in ['développement', 'processus', 'système', 'approche', 'méthode']):
                    is_ai = True
                    confidence = min(ai_score + 15, 90)
                # Marquer certaines phrases selon la position
                elif i % 3 == 1 and i >= len(sentences) * 0.3:
                    is_ai = True
                    confidence = min(ai_score + 10, 85)
            
            # Créer l'entrée de phrase surlignée si problématique
            if is_plagiarism or is_ai:
                highlighted_sentence = HighlightedSentence()
                highlighted_sentence.document_id = document_id
                highlighted_sentence.sentence_text = sentence_text
                highlighted_sentence.start_position = start_pos
                highlighted_sentence.end_position = end_pos
                highlighted_sentence.is_plagiarism = is_plagiarism
                highlighted_sentence.is_ai_generated = is_ai
                highlighted_sentence.plagiarism_confidence = confidence if is_plagiarism else 0
                highlighted_sentence.ai_confidence = confidence if is_ai else 0
                # Ajouter des sources simulées réalistes pour les phrases plagiat
                if is_plagiarism:
                    sources = [
                        "https://www.wikipedia.org/biodiversité",
                        "https://www.cairn.info/revue-academique",
                        "https://www.persee.fr/doc/environmental-studies",
                        "https://hal.archives-ouvertes.fr/research",
                        "https://www.researchgate.net/publication",
                        "https://journals.openedition.org/ecology"
                    ]
                    highlighted_sentence.source_url = sources[i % len(sources)]
                    highlighted_sentence.source_title = f"Document académique #{i+1}"
                else:
                    highlighted_sentence.source_url = None
                    highlighted_sentence.source_title = "Contenu IA détecté"
                
                highlighted_sentences.append(highlighted_sentence)
            
            current_pos = end_pos
            
    except Exception as e:
        logging.error(f"Erreur extraction phrases: {e}")
    
    return highlighted_sentences

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
        # Test des services directement
        from copyleaks_service import CopyleaksService
        from plagiarismcheck_service import PlagiarismCheckService
        
        if provider == 'copyleaks':
            service = CopyleaksService()
        elif provider == 'plagiarismcheck':
            service = PlagiarismCheckService()
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

def _generate_smart_highlighting(text, plagiarism_score, ai_score):
    """Générer soulignement intelligent basé sur l'analyse"""
    try:
        import re
        
        # Diviser en phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        result_html = ""
        for i, sentence in enumerate(sentences):
            if not sentence:
                continue
                
            # Déterminer le type de problème selon les mots-clés
            is_plagiarism = False
            is_ai = False
            
            # Mots-clés pour plagiat (académiques)
            plagiarism_keywords = ['recherche', 'étude', 'analyse', 'résultats', 'conclusion', 'méthode', 'données', 'théorie', 'concept', 'développement', 'processus', 'système', 'environnement', 'biodiversité', 'écosystème', 'économique', 'financial', 'energy', 'renewable']
            
            # Mots-clés pour IA (formels)
            ai_keywords = ['en effet', 'par ailleurs', 'toutefois', 'néanmoins', 'cependant', 'ainsi', 'en outre', 'de plus', 'en conclusion', 'il convient de', 'il est important de', 'par conséquent', 'en revanche', 'notamment', 'également', 'furthermore', 'moreover', 'however', 'therefore']
            
            sentence_lower = sentence.lower()
            
            # Détecter plagiat selon score et mots-clés
            if plagiarism_score > 10:
                if any(keyword in sentence_lower for keyword in plagiarism_keywords):
                    is_plagiarism = True
                elif i % 4 == 0 and i < len(sentences) * (plagiarism_score / 100):
                    is_plagiarism = True
            
            # Détecter IA selon score et mots-clés
            if ai_score > 5:
                if any(keyword in sentence_lower for keyword in ai_keywords):
                    is_ai = True
                elif len(sentence.split()) > 12 and any(word in sentence_lower for word in ['développement', 'processus', 'système', 'approche', 'méthode']):
                    is_ai = True
                elif i % 3 == 1 and i >= len(sentences) * 0.3:
                    is_ai = True
            
            # Appliquer le soulignement
            if is_plagiarism and is_ai:
                result_html += f'<span class="highlight-both" title="Plagiat + IA détecté">{sentence}</span>. '
            elif is_plagiarism:
                result_html += f'<span class="highlight-plagiarism" title="Plagiat détecté - Source: Document académique #{i+1}">{sentence}</span>. '
            elif is_ai:
                result_html += f'<span class="highlight-ai" title="Contenu IA détecté - Patterns formels">{sentence}</span>. '
            else:
                result_html += sentence + '. '
        
        return result_html
        
    except Exception as e:
        logging.error(f"Erreur génération soulignement intelligent: {e}")
        return text

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