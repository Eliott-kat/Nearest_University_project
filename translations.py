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
            'welcome_title': 'Bienvenue sur AcadCheck',
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
            'welcome_title': 'Welcome to AcadCheck',
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