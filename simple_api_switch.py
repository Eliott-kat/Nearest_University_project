"""
Service simple pour basculer entre APIs de plagiat
"""
import os
import logging
from copyleaks_service import CopyleaksService

# Instance du service Copyleaks existant
copyleaks_service = CopyleaksService()

def get_active_service():
    """Retourne le service actif selon la configuration"""
    provider = os.environ.get('PLAGIARISM_API_PROVIDER', 'copyleaks').lower()
    
    if provider == 'plagiarismcheck':
        # Pour l'instant, on garde Copyleaks mais on peut étendre plus tard
        logging.info("Provider configuré : PlagiarismCheck (utilisation future)")
        return copyleaks_service
    else:
        logging.info("Provider configuré : Copyleaks")
        return copyleaks_service

def get_provider_status():
    """Obtenir le statut du provider actuel"""
    provider = os.environ.get('PLAGIARISM_API_PROVIDER', 'copyleaks').lower()
    copyleaks_configured = bool(os.environ.get('COPYLEAKS_EMAIL') and os.environ.get('COPYLEAKS_API_KEY'))
    plagiarismcheck_configured = bool(os.environ.get('PLAGIARISMCHECK_API_TOKEN'))
    
    return {
        'current_provider': provider,
        'copyleaks_configured': copyleaks_configured,
        'plagiarismcheck_configured': plagiarismcheck_configured,
        'ready_to_switch': plagiarismcheck_configured and provider == 'copyleaks'
    }