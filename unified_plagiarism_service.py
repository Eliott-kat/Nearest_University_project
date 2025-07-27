"""
Service unifié pour la détection de plagiat - supporte plusieurs APIs
"""
import logging
from typing import Optional
# Configuration simplifiée - plus besoin d'APIConfig
from copyleaks_service import CopyleaksService
from gptzero_service_class import GPTZeroService
from models import Document

class UnifiedPlagiarismService:
    """Service unifié qui bascule automatiquement entre APIs"""
    
    def __init__(self):
        self.copyleaks_service = CopyleaksService()
        self.gptzero_service = GPTZeroService()
        self._services = []
        self._current_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialiser les services avec fallback simple Copyleaks → GPTZero"""
        # Toujours commencer par Copyleaks, fallback vers GPTZero
        self._services = [
            self.copyleaks_service,
            self.gptzero_service
        ]
        
        self._current_service = self._services[0]
        logging.info("Service principal: Copyleaks, fallback: GPTZero")
    
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
        elif service == self.gptzero_service:
            return "GPTZero"
        else:
            return "Unknown"
    
    def get_api_status(self) -> dict:
        """Obtenir le statut détaillé des APIs"""
        # Tester la connectivité
        copyleaks_working = False
        gptzero_working = False
        
        try:
            copyleaks_working = self.copyleaks_service.authenticate()
        except:
            pass
        
        try:
            gptzero_working = self.gptzero_service.authenticate()
        except:
            pass
        
        return {
            'copyleaks_configured': bool(self.copyleaks_service.email and self.copyleaks_service.api_key),
            'gptzero_configured': self.gptzero_service.is_configured(),
            'copyleaks_working': copyleaks_working,
            'gptzero_working': gptzero_working,
            'current_service': self.get_current_provider_name(),
            'fallback_order': 'Copyleaks → GPTZero → Demo',
            'recommendations': self._get_recommendations(copyleaks_working, gptzero_working)
        }
    
    def _get_recommendations(self, copyleaks_working: bool, gptzero_working: bool) -> list:
        """Générer des recommandations basées sur l'état des APIs"""
        recommendations = []
        
        if not copyleaks_working and not gptzero_working:
            recommendations.append("Aucune API fonctionnelle - Mode démonstration activé")
            recommendations.append("Configurez COPYLEAKS_API_KEY ou GPTZERO_API_KEY dans .env")
        elif copyleaks_working and not gptzero_working:
            recommendations.append("Seule l'API Copyleaks fonctionne - GPTZero disponible comme fallback")
        elif not copyleaks_working and gptzero_working:
            recommendations.append("Seule GPTZero fonctionne - Considérez configurer Copyleaks")
        else:
            recommendations.append("Toutes les APIs fonctionnent correctement")
        
        return recommendations

# Instance globale
unified_service = UnifiedPlagiarismService()