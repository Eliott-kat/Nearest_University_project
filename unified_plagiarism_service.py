"""
Service unifié pour la détection de plagiat - supporte plusieurs APIs
"""
import logging
from typing import Optional
from api_config import APIConfig, APIProvider
from copyleaks_service import CopyleaksService
from plagiarismcheck_service import PlagiarismCheckService
from gptzero_service_class import GPTZeroService
from models import Document

class UnifiedPlagiarismService:
    """Service unifié qui bascule automatiquement entre APIs"""
    
    def __init__(self):
        self.copyleaks_service = CopyleaksService()
        self.plagiarismcheck_service = PlagiarismCheckService()
        self.gptzero_service = GPTZeroService()
        self._services = []
        self._current_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialiser les services avec fallback en cascade"""
        current_provider = APIConfig.get_current_provider()
        
        # Ordre de fallback : Principal → PlagiarismCheck → GPTZero → Demo
        if current_provider == APIProvider.COPYLEAKS:
            self._services = [
                self.copyleaks_service,
                self.plagiarismcheck_service, 
                self.gptzero_service
            ]
        else:
            self._services = [
                self.plagiarismcheck_service,
                self.copyleaks_service,
                self.gptzero_service
            ]
        
        self._current_service = self._services[0]
        logging.info(f"Service principal: {current_provider.value}, fallback: PlagiarismCheck → GPTZero")
    
    def authenticate(self) -> bool:
        """Authentifier avec fallback en cascade sur tous les services"""
        for i, service in enumerate(self._services):
            service_name = self._get_service_name(service)
            
            try:
                if service.authenticate():
                    if i > 0:  # Si ce n'est pas le service principal
                        logging.info(f"Basculement vers {service_name} réussi")
                        self._current_service = service
                    return True
                else:
                    logging.warning(f"Échec authentification {service_name}")
                    
            except Exception as e:
                logging.error(f"Erreur authentification {service_name}: {str(e)}")
        
        logging.warning("Tous les services ont échoué, utilisation du mode démonstration")
        return False
    
    def submit_document(self, document: Document) -> bool:
        """Soumettre un document avec fallback en cascade"""
        for i, service in enumerate(self._services):
            service_name = self._get_service_name(service)
            
            try:
                if service.submit_document(document):
                    if i > 0:  # Si basculement nécessaire
                        logging.info(f"Soumission réussie avec {service_name} après basculement")
                        self._current_service = service
                    return True
                else:
                    logging.warning(f"Échec soumission avec {service_name}")
                    
            except Exception as e:
                logging.error(f"Erreur soumission {service_name}: {str(e)}")
        
        logging.error("Tous les services ont échoué pour la soumission")
        return False
    
    def get_current_provider_name(self) -> str:
        """Obtenir le nom du provider actuel"""
        return self._get_service_name(self._current_service)
    
    def _get_service_name(self, service) -> str:
        """Obtenir le nom d'un service"""
        if service == self.copyleaks_service:
            return "Copyleaks"
        elif service == self.plagiarismcheck_service:
            return "PlagiarismCheck"
        elif service == self.gptzero_service:
            return "GPTZero"
        else:
            return "Unknown"
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