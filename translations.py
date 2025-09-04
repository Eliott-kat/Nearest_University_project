"""
Système de traduction pour AcadCheck - Support FR/EN
"""

class Translations:
    """Gestionnaire des traductions FR/EN"""
    
    TRANSLATIONS = {
        'fr': {
            # Navigation
            'home': 'Accueil',
            'dashboard': 'Tableau de bord',
            'upload': 'Télécharger',
            'reports': 'Rapports',
            'settings': 'Paramètres',
            'logout': 'Déconnexion',
            'login': 'Connexion',
            'profile': 'Profil',
            
            # Page d'accueil
            'welcome_title': 'Bienvenue sur {brand}',
            'welcome_subtitle': 'Plateforme d\'intégrité académique',
            'welcome_description': 'Analysez vos documents pour détecter le plagiat et le contenu généré par IA avec notre technologie avancée.',
            'get_started': 'Commencer',
            'learn_more': 'En savoir plus',
            
            # Upload de documents
            'upload_document': 'Télécharger un document',
            'drag_drop_files': 'Glissez-déposez vos fichiers ici ou cliquez pour sélectionner',
            'supported_formats': 'Formats supportés: PDF, DOCX, TXT',
            'max_file_size': 'Taille maximale: 10 MB',
            'analyze_button': 'Analyser le document',
            'uploading': 'Téléchargement en cours...',
            'analyzing': 'Analyse en cours...',
            
            # Résultats d'analyse
            'analysis_results': 'Résultats d\'analyse',
            'plagiarism_score': 'Score de plagiat',
            'ai_detection_score': 'Score de détection IA',
            'overall_similarity': 'Similarité globale',
            'provider_used': 'Service utilisé',
            'analysis_date': 'Date d\'analyse',
            'download_report': 'Télécharger le rapport',
            'view_details': 'Voir les détails',
            
            # Statuts
            'status_pending': 'En attente',
            'status_processing': 'En cours de traitement',
            'status_completed': 'Terminé',
            'status_failed': 'Échec',
            'status_demo': 'Mode démonstration',
            
            # Erreurs et messages
            'error_upload_failed': 'Échec du téléchargement',
            'error_file_too_large': 'Fichier trop volumineux',
            'error_unsupported_format': 'Format non supporté',
            'error_analysis_failed': 'Échec de l\'analyse',
            'success_upload': 'Document téléchargé avec succès',
            'success_analysis': 'Analyse terminée avec succès',
            'no_documents': 'Aucun document trouvé',
            
            # API Status
            'api_status': 'État des APIs',
            'copyleaks_status': 'Copyleaks',
            'gptzero_status': 'GPTZero',
            'configured': 'Configuré',
            'not_configured': 'Non configuré',
            'working': 'Fonctionnel',
            'not_working': 'Hors service',
            'demo_mode': 'Mode démonstration',
            
            # Rapports
            'report_title': 'Rapport d\'analyse',
            'document_info': 'Informations du document',
            'filename': 'Nom du fichier',
            'file_size': 'Taille',
            'upload_date': 'Date de téléchargement',
            'analysis_summary': 'Résumé de l\'analyse',
            'highlighted_sentences': 'Phrases suspectes',
            'confidence_level': 'Niveau de confiance',
            
            # Boutons et actions
            'submit': 'Soumettre',
            'cancel': 'Annuler',
            'save': 'Enregistrer',
            'delete': 'Supprimer',
            'edit': 'Modifier',
            'close': 'Fermer',
            'refresh': 'Actualiser',
            'back': 'Retour',
            'next': 'Suivant',
            'previous': 'Précédent',
            
            # Footer
            'powered_by': 'Propulsé par',
            'academic_integrity': 'Intégrité académique',
            'version': 'Version',
            'copyright': 'Tous droits réservés',
            
            # Language messages
            'language_changed': 'Langue changée avec succès',
            'language_not_supported': 'Langue non supportée',
            
            # Éléments manquants du dashboard
            'recent_documents': 'Documents récents',
            'quick_actions': 'Actions rapides',
            'statistics': 'Statistiques',
            'total_documents': 'Documents totaux',
            'documents_analyzed': 'Documents analysés',
            'average_plagiarism': 'Plagiat moyen',
            'average_ai_score': 'Score IA moyen',
            'upload_new_document': 'Télécharger un nouveau document',
            'view_all_reports': 'Voir tous les rapports',
            'no_recent_documents': 'Aucun document récent',
            'get_started_upload': 'Commencez par télécharger votre premier document',
            
            # Upload page
            'select_file': 'Sélectionner un fichier',
            'file_selected': 'Fichier sélectionné',
            'processing': 'Traitement en cours',
            'upload_success': 'Téléchargement réussi',
            'upload_error': 'Erreur de téléchargement',
            'file_too_large_detailed': 'Le fichier est trop volumineux. Taille maximale autorisée : 10 MB',
            'unsupported_format_detailed': 'Format de fichier non supporté. Formats acceptés : PDF, DOCX, TXT',
            
            # Report page
            'document_analysis': 'Analyse du document',
            'plagiarism_detected': 'Plagiat détecté',
            'ai_content_detected': 'Contenu IA détecté',
            'sources_found': 'Sources trouvées',
            'suspicious_sentences': 'Phrases suspectes',
            'clean_content': 'Contenu authentique',
            'methodology': 'Méthodologie',
            'detection_method': 'Méthode de détection',
            'analysis_confidence': 'Confiance de l\'analyse',
            'high_confidence': 'Confiance élevée',
            'medium_confidence': 'Confiance moyenne',
            'low_confidence': 'Confiance faible',
            
            # Histoire des documents
            'document_history': 'Historique des documents',
            'analysis_history': 'Historique des analyses',
            'recent_uploads': 'Téléchargements récents',
            'filter_by_date': 'Filtrer par date',
            'filter_by_type': 'Filtrer par type',
            'search_documents': 'Rechercher dans les documents',
            
            # Authentification  
            'register': 'S\'inscrire',
            'sign_in': 'Se connecter',
            'sign_up': 'S\'inscrire',
            'create_account': 'Créer un compte',
            'forgot_password': 'Mot de passe oublié',
            'remember_me': 'Se souvenir de moi',
            'username': 'Nom d\'utilisateur',
            'email': 'Email',
            'password': 'Mot de passe',
            'confirm_password': 'Confirmer le mot de passe',
            
            # Messages système
            'loading': 'Chargement...',
            'please_wait': 'Veuillez patienter',
            'success': 'Succès',
            'error': 'Erreur',
            'warning': 'Attention',
            'info': 'Information',
            'confirm': 'Confirmer',
            'yes': 'Oui',
            'no': 'Non',
        },
        
        'en': {
            # Navigation
            'home': 'Home',
            'dashboard': 'Dashboard', 
            'upload': 'Upload',
            'reports': 'Reports',
            'settings': 'Settings',
            'logout': 'Logout',
            'login': 'Login',
            'profile': 'Profile',
            
            # Homepage
            'welcome_title': 'Welcome to {brand}',
            'welcome_subtitle': 'Academic Integrity Platform',
            'welcome_description': 'Analyze your documents for plagiarism and AI-generated content with our advanced technology.',
            'get_started': 'Get Started',
            'learn_more': 'Learn More',
            
            # Document upload
            'upload_document': 'Upload Document',
            'drag_drop_files': 'Drag and drop your files here or click to select',
            'supported_formats': 'Supported formats: PDF, DOCX, TXT',
            'max_file_size': 'Maximum size: 10 MB',
            'analyze_button': 'Analyze Document',
            'uploading': 'Uploading...',
            'analyzing': 'Analyzing...',
            
            # Analysis results
            'analysis_results': 'Analysis Results',
            'plagiarism_score': 'Plagiarism Score',
            'ai_detection_score': 'AI Detection Score',
            'overall_similarity': 'Overall Similarity',
            'provider_used': 'Provider Used',
            'analysis_date': 'Analysis Date',
            'download_report': 'Download Report',
            'view_details': 'View Details',
            
            # Status
            'status_pending': 'Pending',
            'status_processing': 'Processing',
            'status_completed': 'Completed',
            'status_failed': 'Failed',
            'status_demo': 'Demo Mode',
            
            # Errors and messages
            'error_upload_failed': 'Upload failed',
            'error_file_too_large': 'File too large',
            'error_unsupported_format': 'Unsupported format',
            'error_analysis_failed': 'Analysis failed',
            'success_upload': 'Document uploaded successfully',
            'success_analysis': 'Analysis completed successfully',
            'no_documents': 'No documents found',
            
            # API Status
            'api_status': 'API Status',
            'copyleaks_status': 'Copyleaks',
            'gptzero_status': 'GPTZero',
            'configured': 'Configured',
            'not_configured': 'Not Configured',
            'working': 'Working',
            'not_working': 'Not Working',
            'demo_mode': 'Demo Mode',
            
            # Reports
            'report_title': 'Analysis Report',
            'document_info': 'Document Information',
            'filename': 'Filename',
            'file_size': 'File Size',
            'upload_date': 'Upload Date',
            'analysis_summary': 'Analysis Summary',
            'highlighted_sentences': 'Suspicious Sentences',
            'confidence_level': 'Confidence Level',
            
            # Buttons and actions
            'submit': 'Submit',
            'cancel': 'Cancel',
            'save': 'Save',
            'delete': 'Delete',
            'edit': 'Edit',
            'close': 'Close',
            'refresh': 'Refresh',
            'back': 'Back',
            'next': 'Next',
            'previous': 'Previous',
            
            # Footer
            'powered_by': 'Powered by',
            'academic_integrity': 'Academic Integrity',
            'version': 'Version',
            'copyright': 'All rights reserved',
            
            # Language messages
            'language_changed': 'Language changed successfully',
            'language_not_supported': 'Language not supported',
            
            # Missing dashboard elements
            'recent_documents': 'Recent Documents',
            'quick_actions': 'Quick Actions',
            'statistics': 'Statistics',
            'total_documents': 'Total Documents',
            'documents_analyzed': 'Documents Analyzed',
            'average_plagiarism': 'Average Plagiarism',
            'average_ai_score': 'Average AI Score',
            'upload_new_document': 'Upload New Document',
            'view_all_reports': 'View All Reports',
            'no_recent_documents': 'No recent documents',
            'get_started_upload': 'Get started by uploading your first document',
            
            # Upload page
            'select_file': 'Select File',
            'file_selected': 'File Selected',
            'processing': 'Processing',
            'upload_success': 'Upload Successful',
            'upload_error': 'Upload Error',
            'file_too_large_detailed': 'File is too large. Maximum allowed size: 10 MB',
            'unsupported_format_detailed': 'Unsupported file format. Accepted formats: PDF, DOCX, TXT',
            
            # Report page
            'document_analysis': 'Document Analysis',
            'plagiarism_detected': 'Plagiarism Detected',
            'ai_content_detected': 'AI Content Detected',
            'sources_found': 'Sources Found',
            'suspicious_sentences': 'Suspicious Sentences',
            'clean_content': 'Clean Content',
            'methodology': 'Methodology',
            'detection_method': 'Detection Method',
            'analysis_confidence': 'Analysis Confidence',
            'high_confidence': 'High Confidence',
            'medium_confidence': 'Medium Confidence',
            'low_confidence': 'Low Confidence',
            
            # Document history
            'document_history': 'Document History',
            'analysis_history': 'Analysis History',
            'recent_uploads': 'Recent Uploads',
            'filter_by_date': 'Filter by Date',
            'filter_by_type': 'Filter by Type',
            'search_documents': 'Search Documents',
            
            # Authentication
            'register': 'Register',
            'sign_in': 'Sign In',
            'sign_up': 'Sign Up',
            'create_account': 'Create Account',
            'forgot_password': 'Forgot Password',
            'remember_me': 'Remember Me',
            'username': 'Username',
            'email': 'Email',
            'password': 'Password',
            'confirm_password': 'Confirm Password',
            
            # System messages
            'loading': 'Loading...',
            'please_wait': 'Please wait',
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information',
            'confirm': 'Confirm',
            'yes': 'Yes',
            'no': 'No',
        }
    }
    
    @classmethod
    def get(cls, key: str, language: str = 'fr') -> str:
        """Récupérer une traduction"""
        if language not in cls.TRANSLATIONS:
            language = 'fr'  # Fallback vers français
            
        return cls.TRANSLATIONS[language].get(key, key)
    
    @classmethod
    def get_available_languages(cls) -> dict:
        """Obtenir la liste des langues disponibles"""
        return {
            'fr': 'Français',
            'en': 'English'
        }