"""
Service unifié pour la détection de plagiat - supporte plusieurs APIs
"""
import logging
from typing import Optional
from api_config import APIConfig, APIProvider
from copyleaks_service import CopyleaksService
from plagiarismcheck_service import PlagiarismCheckService
from models import Document

class UnifiedPlagiarismService:
    """Service unifié qui bascule automatiquement entre APIs"""
    
    def __init__(self):
        self.copyleaks_service = CopyleaksService()
        self.plagiarismcheck_service = PlagiarismCheckService()
        self._current_service = None
        self._fallback_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialiser les services selon la configuration"""
        current_provider = APIConfig.get_current_provider()
        
        if current_provider == APIProvider.COPYLEAKS:
            self._current_service = self.copyleaks_service
            self._fallback_service = self.plagiarismcheck_service
        else:
            self._current_service = self.plagiarismcheck_service
            self._fallback_service = self.copyleaks_service
        
        logging.info(f"Service principal: {current_provider.value}")
    
    def authenticate(self) -> bool:
        """Authentifier avec le service principal, fallback si échec"""
        # Tenter avec le service principal
        if self._current_service.authenticate():
            return True
        
        logging.warning(f"Échec authentification service principal, tentative fallback")
        
        # Tenter avec le service de fallback
        if self._fallback_service.authenticate():
            # Basculer vers le fallback
            self._current_service, self._fallback_service = self._fallback_service, self._current_service
            logging.info("Basculement vers service de fallback réussi")
            return True
        
        logging.warning("Tous les services ont échoué, utilisation du mode démonstration")
        return False
    
    def submit_document(self, document: Document) -> bool:
        """Soumettre un document avec fallback automatique"""
        # Tenter avec le service principal
        if self._current_service.submit_document(document):
            return True
        
        logging.warning("Échec soumission service principal, tentative fallback")
        
        # Tenter avec le service de fallback
        if self._fallback_service.submit_document(document):
            # Basculer vers le fallback pour les prochaines requêtes
            self._current_service, self._fallback_service = self._fallback_service, self._current_service
            logging.info("Basculement vers service de fallback pour soumission")
            return True
        
        logging.error("Tous les services ont échoué pour la soumission")
        return False
    
    def get_current_provider_name(self) -> str:
        """Obtenir le nom du provider actuel"""
        if self._current_service == self.copyleaks_service:
            return "Copyleaks"
        elif self._current_service == self.plagiarismcheck_service:
            return "PlagiarismCheck"
        else:
            return "Demo"
    
    def get_api_status(self) -> dict:
        """Obtenir le statut détaillé des APIs"""
        config_status = APIConfig.get_provider_status()
        
        # Tester la connectivité
        copyleaks_working = False
        plagiarismcheck_working = False
        
        try:
            copyleaks_working = self.copyleaks_service.authenticate()
        except:
            pass
        
        try:
            plagiarismcheck_working = self.plagiarismcheck_service.authenticate()
        except:
            pass
        
        return {
            **config_status,
            'copyleaks_working': copyleaks_working,
            'plagiarismcheck_working': plagiarismcheck_working,
            'current_service': self.get_current_provider_name(),
            'recommendations': self._get_recommendations(copyleaks_working, plagiarismcheck_working)
        }
    
    def _get_recommendations(self, copyleaks_working: bool, plagiarismcheck_working: bool) -> list:
        """Générer des recommandations basées sur l'état des APIs"""
        recommendations = []
        
        if not copyleaks_working and not plagiarismcheck_working:
            recommendations.append("Aucune API fonctionnelle - Mode démonstration activé")
        elif copyleaks_working and not plagiarismcheck_working:
            recommendations.append("Seule l'API Copyleaks fonctionne")
        elif not copyleaks_working and plagiarismcheck_working:
            recommendations.append("Seule l'API PlagiarismCheck fonctionne - Considérez le basculement")
        else:
            recommendations.append("Toutes les APIs fonctionnent correctement")
        
        return recommendations

# Instance globale
unified_service = UnifiedPlagiarismService()