"""
Configuration centralisée pour les APIs de détection de plagiat
"""
import os
from enum import Enum

class APIProvider(Enum):
    COPYLEAKS = "copyleaks"
    PLAGIARISMCHECK = "plagiarismcheck"

class APIConfig:
    """Configuration centralisée pour basculer entre APIs"""
    
    # Provider actuel (peut être changé dans .env)
    CURRENT_PROVIDER = os.environ.get('PLAGIARISM_API_PROVIDER', 'copyleaks').lower()
    
    # Configuration Copyleaks
    COPYLEAKS_EMAIL = os.environ.get('COPYLEAKS_EMAIL')
    COPYLEAKS_API_KEY = os.environ.get('COPYLEAKS_API_KEY')
    
    # Configuration PlagiarismCheck
    PLAGIARISMCHECK_API_TOKEN = os.environ.get('PLAGIARISMCHECK_API_TOKEN')
    
    @classmethod
    def get_current_provider(cls) -> APIProvider:
        """Obtenir le provider actuel"""
        if cls.CURRENT_PROVIDER == 'plagiarismcheck':
            return APIProvider.PLAGIARISMCHECK
        else:
            return APIProvider.COPYLEAKS
    
    @classmethod
    def is_provider_configured(cls, provider: APIProvider) -> bool:
        """Vérifier si un provider est configuré"""
        if provider == APIProvider.COPYLEAKS:
            return bool(cls.COPYLEAKS_EMAIL and cls.COPYLEAKS_API_KEY)
        elif provider == APIProvider.PLAGIARISMCHECK:
            return bool(cls.PLAGIARISMCHECK_API_TOKEN)
        return False
    
    @classmethod
    def get_provider_status(cls) -> dict:
        """Obtenir le statut de tous les providers"""
        return {
            'current': cls.get_current_provider().value,
            'copyleaks_configured': cls.is_provider_configured(APIProvider.COPYLEAKS),
            'plagiarismcheck_configured': cls.is_provider_configured(APIProvider.PLAGIARISMCHECK),
            'available_providers': [
                provider.value for provider in APIProvider 
                if cls.is_provider_configured(provider)
            ]
        }