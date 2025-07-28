"""
Service simple pour basculer entre APIs de plagiat avec fallback automatique
"""
import os
import logging
from copyleaks_service import CopyleaksService
from plagiarismcheck_service import PlagiarismCheckService


class SmartAPISwitch:
    """Service intelligent qui teste les APIs avec fallback automatique"""
    
    def __init__(self):
        self.copyleaks_service = CopyleaksService()
        self.plagiarismcheck_service = PlagiarismCheckService()

        self._current_service = None
        self._last_working_service = None
        self._initialize_primary_service()
    
    def _initialize_primary_service(self):
        """Initialiser le service principal selon la configuration"""
        provider = os.environ.get('PLAGIARISM_API_PROVIDER', 'copyleaks').lower()
        
        if provider == 'plagiarismcheck':
            self._current_service = self.plagiarismcheck_service
            logging.info("Provider configuré : PlagiarismCheck")
        else:
            self._current_service = self.copyleaks_service
            logging.info("Provider configuré : Copyleaks")
    
    def authenticate(self):
        """Authentifier avec fallback automatique"""
        # Tenter avec le service principal
        if self._current_service.authenticate():
            self._last_working_service = self._current_service
            return True
        
        # Fallback vers les autres services
        fallback_services = self._get_fallback_services()
        for fallback_service in fallback_services:
            if fallback_service and fallback_service.authenticate():
                logging.warning(f"Service principal échoué, basculement vers {self._get_service_name(fallback_service)}")
                self._current_service = fallback_service
                self._last_working_service = fallback_service
                return True
        
        logging.warning("Tous les services ont échoué, utilisation du mode démonstration")
        return False
    
    def submit_document(self, document):
        """Soumettre un document avec fallback automatique"""
        # Tenter avec le service principal
        if self._current_service.submit_document(document):
            self._last_working_service = self._current_service
            return True
        
        # Fallback vers les autres services
        fallback_services = self._get_fallback_services()
        for fallback_service in fallback_services:
            if fallback_service:
                logging.warning(f"Service principal échoué, tentative avec {self._get_service_name(fallback_service)}")
                if fallback_service.submit_document(document):
                    logging.info(f"Basculement réussi vers {self._get_service_name(fallback_service)}")
                    self._current_service = fallback_service
                    self._last_working_service = fallback_service
                    return True
        
        logging.error("Tous les services ont échoué pour la soumission")
        return False
    
    def _get_fallback_services(self):
        """Obtenir la liste des services de fallback"""
        fallback_services = []
        all_services = [self.copyleaks_service, self.plagiarismcheck_service]
        
        # Exclure le service actuel et ajouter les autres services configurés
        for service in all_services:
            if service != self._current_service and self._is_service_configured(service):
                fallback_services.append(service)
        
        return fallback_services
    
    def _is_service_configured(self, service):
        """Vérifier si un service est configuré"""
        if service == self.copyleaks_service:
            return bool(os.environ.get('COPYLEAKS_EMAIL') and os.environ.get('COPYLEAKS_API_KEY'))
        elif service == self.plagiarismcheck_service:
            return bool(os.environ.get('PLAGIARISMCHECK_API_TOKEN'))

        return False
    
    def _get_service_name(self, service):
        """Obtenir le nom du service"""
        if service == self.copyleaks_service:
            return "Copyleaks"
        elif service == self.plagiarismcheck_service:
            return "PlagiarismCheck"

        return "Unknown"
    
    @property
    def token(self):
        """Propriété pour vérifier si le service actuel a un token"""
        return getattr(self._current_service, 'token', None)

# Instance globale
_smart_switch = SmartAPISwitch()

def get_active_service():
    """Retourne le service actif avec fallback intelligent"""
    return _smart_switch

def get_provider_status():
    """Obtenir le statut du provider actuel"""
    provider = os.environ.get('PLAGIARISM_API_PROVIDER', 'copyleaks').lower()
    copyleaks_configured = bool(os.environ.get('COPYLEAKS_EMAIL') and os.environ.get('COPYLEAKS_API_KEY'))
    plagiarismcheck_configured = bool(os.environ.get('PLAGIARISMCHECK_API_TOKEN'))
    
    return {
        'current_provider': provider,
        'copyleaks_configured': copyleaks_configured,
        'plagiarismcheck_configured': plagiarismcheck_configured,
        'total_providers': 2,
        'available_providers': sum([copyleaks_configured, plagiarismcheck_configured])
    }

def get_service_details():
    """Obtenir les détails des services"""
    return {
        'copyleaks': {
            'name': 'Copyleaks',
            'description': 'Service professionnel de détection de plagiat avec IA intégrée',
            'features': ['Plagiarism Detection', 'AI Detection', 'Multi-language Support'],
            'configured': bool(os.environ.get('COPYLEAKS_EMAIL') and os.environ.get('COPYLEAKS_API_KEY')),
            'status': 'Configured' if bool(os.environ.get('COPYLEAKS_EMAIL') and os.environ.get('COPYLEAKS_API_KEY')) else 'Not Configured'
        },
        'plagiarismcheck': {
            'name': 'PlagiarismCheck',
            'description': 'Service de vérification de plagiat rapide et précis',
            'features': ['Plagiarism Detection', 'Fast Processing', 'Academic Focus'],
            'configured': bool(os.environ.get('PLAGIARISMCHECK_API_TOKEN')),
            'status': 'Configured' if bool(os.environ.get('PLAGIARISMCHECK_API_TOKEN')) else 'Not Configured'
        }
    }