"""
Utilitaires pour la gestion des langues dans AcadCheck
"""
from flask import session, request
try:
    from translations import Translations
except ImportError:
    # Fallback si translations.py n'est pas disponible
    class Translations:
        @classmethod
        def get(cls, key, language='fr'):
            return key
        @classmethod
        def get_available_languages(cls):
            return {'fr': 'Français', 'en': 'English'}

class LanguageManager:
    """Gestionnaire de langue pour l'application"""
    
    DEFAULT_LANGUAGE = 'en'
    SUPPORTED_LANGUAGES = ['fr', 'en']
    
    @classmethod
    def get_current_language(cls) -> str:
        """Toujours retourner l'anglais comme langue par défaut, sauf si la session impose autre chose"""
        if 'language' in session and session['language'] in cls.SUPPORTED_LANGUAGES:
            return session['language']
        # Forcer l'anglais par défaut
        cls.set_language('en')
        return 'en'
    
    @classmethod
    def set_language(cls, language: str) -> bool:
        """Définir la langue de l'utilisateur"""
        if language in cls.SUPPORTED_LANGUAGES:
            session['language'] = language
            session.permanent = True
            return True
        return False
    
    @classmethod
    def translate(cls, key: str, language: str = None) -> str:
        """Traduire une clé selon la langue actuelle"""
        if language is None:
            language = cls.get_current_language()
        return Translations.get(key, language or 'fr')
    
    @classmethod
    def get_language_switcher_data(cls) -> dict:
        """Obtenir les données pour le sélecteur de langue"""
        current_lang = cls.get_current_language()
        available_langs = Translations.get_available_languages()
        
        return {
            'current': current_lang,
            'current_name': available_langs[current_lang],
            'available': available_langs,
            'other': [lang for lang in available_langs.keys() if lang != current_lang]
        }

def init_app(app):
    """Initialiser le support des langues dans Flask"""
    
    @app.context_processor
    def inject_language_vars():
        """Injecter les variables de langue dans tous les templates"""
        return {
            'current_language': LanguageManager.get_current_language(),
            'language_switcher': LanguageManager.get_language_switcher_data(),
            '_': LanguageManager.translate,  # Fonction de traduction courte
            'get_text': LanguageManager.translate  # Alias plus explicite
        }
    
    @app.route('/set-language/<language>')
    def set_language(language):
        """Route pour changer de langue"""
        from flask import redirect, url_for, flash
        
        if LanguageManager.set_language(language):
            flash(LanguageManager.translate('language_changed', language), 'success')
        else:
            flash(LanguageManager.translate('language_not_supported', language), 'error')
        
        # Rediriger vers la page précédente ou l'accueil
        return redirect(request.referrer or url_for('index'))