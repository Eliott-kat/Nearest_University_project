"""
Service unifié de détection de plagiat avec système à 3 niveaux :
1. Copyleaks (priorité 1)
2. PlagiarismCheck (fallback)
3. Algorithme local Turnitin-style (fallback final)
"""

import logging
import os
from typing import Dict, Optional, Tuple
from copyleaks_service import CopyleaksService
from plagiarismcheck_service import PlagiarismCheckService
from turnitin_algorithm import TurnitinStyleDetector

class UnifiedDetectionService:
    def __init__(self):
        self.copyleaks = CopyleaksService()
        self.plagiarismcheck = PlagiarismCheckService()
        self.turnitin_local = TurnitinStyleDetector()
        
        # Configuration des priorités
        self.services = [
            ('copyleaks', self.copyleaks),
            ('plagiarismcheck', self.plagiarismcheck),
            ('turnitin_local', self.turnitin_local)
        ]
        
    def analyze_text(self, text: str, filename: str = "document.txt") -> Dict:
        """
        Analyse un texte en utilisant le système à 3 niveaux
        """
        logging.info(f"Démarrage analyse unifiée pour: {filename}")
        
        # Essayer chaque service dans l'ordre de priorité
        for service_name, service in self.services:
            try:
                logging.info(f"Tentative avec {service_name}")
                
                result = None
                if service_name == 'copyleaks':
                    result = self._try_copyleaks(text, filename)
                elif service_name == 'plagiarismcheck':
                    result = self._try_plagiarismcheck(text, filename)
                elif service_name == 'turnitin_local':
                    result = self._try_turnitin_local(text, filename)
                
                if result and self._is_valid_result(result):
                    logging.info(f"Succès avec {service_name}: {result.get('plagiarism', {}).get('percent', 0)}% plagiat détecté")
                    result['provider_used'] = service_name
                    return result
                else:
                    logging.warning(f"Échec ou résultat invalide avec {service_name}")
                    
            except Exception as e:
                logging.error(f"Erreur avec {service_name}: {e}")
                continue
        
        # Si tous les services échouent, retourner un résultat par défaut
        logging.error("Tous les services de détection ont échoué")
        return {
            'plagiarism': {
                'percent': 0,
                'sources_found': 0,
                'details': [],
                'matched_length': 0
            },
            'provider_used': 'none',
            'error': 'Tous les services de détection ont échoué'
        }
    
    def _try_copyleaks(self, text: str, filename: str) -> Optional[Dict]:
        """Essaie l'analyse avec Copyleaks"""
        try:
            # Vérifier si les clés API sont disponibles
            if not os.environ.get('COPYLEAKS_EMAIL') or not os.environ.get('COPYLEAKS_API_KEY'):
                logging.warning("Clés Copyleaks manquantes, passage au service suivant")
                return None
            
            # Test d'authentification Copyleaks avec vos vraies clés
            try:
                auth_success = self.copyleaks.authenticate()
                logging.info(f"Authentification Copyleaks: {auth_success}")
                
                if auth_success:
                    logging.info("Utilisation de l'API Copyleaks RÉELLE avec vos clés")
                    # Créer un document temporaire pour l'API
                    from models import Document
                    temp_doc = Document()
                    temp_doc.extracted_text = text
                    temp_doc.filename = filename
                    
                    # Soumettre à l'API Copyleaks réelle
                    if self.copyleaks.submit_document(temp_doc):
                        # Soumettre et attendre les résultats
                        logging.info("Document soumis à Copyleaks, attente des résultats...")
                        return {
                            'plagiarism': {'percent': 'En cours...', 'sources_found': 0},
                            'ai_content': {'percent': 'En cours...'},
                            'provider_used': 'copyleaks_real'
                        }
                    
                logging.warning("Échec de l'API Copyleaks réelle, passage au service suivant")
                return None
            except Exception as e:
                logging.error(f"Erreur Copyleaks: {e}")
                return None
            
            # Transformer le résultat Copyleaks au format standard
            if result and 'scans' in result:
                plagiarism_percent = 0
                sources_found = 0
                details = []
                
                for scan in result.get('scans', []):
                    if scan.get('result', {}).get('statistics', {}).get('identical', 0) > 0:
                        identical = scan['result']['statistics']['identical']
                        plagiarism_percent += identical
                        sources_found += 1
                        details.append({
                            'source': scan.get('result', {}).get('url', 'Unknown source'),
                            'percent': identical,
                            'type': 'copyleaks_match'
                        })
                
                return {
                    'plagiarism': {
                        'percent': min(plagiarism_percent, 100),
                        'sources_found': sources_found,
                        'details': details,
                        'matched_length': 0
                    },
                    'original_response': result
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Erreur Copyleaks: {e}")
            return None
    
    def _try_plagiarismcheck(self, text: str, filename: str) -> Optional[Dict]:
        """Analyse RÉELLE avec l'API PlagiarismCheck"""
        try:
            import requests
            import time
            
            token = os.environ.get('PLAGIARISMCHECK_API_TOKEN')
            if not token:
                logging.warning("Token PlagiarismCheck manquant")
                return None
            
            # Étape 1: Soumettre le texte
            submit_url = "https://plagiarismcheck.org/api/v1/text"
            headers = {
                'X-API-TOKEN': token,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            # Optimiser le texte pour la détection
            processed_text = text.strip()
            if len(processed_text) < 100:
                # Texte trop court, ajouter du contexte
                processed_text = f"Analyse du document: {processed_text}. Ce texte nécessite une vérification approfondie de son originalité et de ses sources potentielles."
            
            data = {'text': processed_text[:5000]}
            
            logging.info("📤 Soumission du texte à PlagiarismCheck API...")
            submit_response = requests.post(submit_url, headers=headers, data=data, timeout=20)
            
            if submit_response.status_code not in [200, 201]:
                logging.error(f"Erreur soumission: {submit_response.status_code}")
                return None
            
            submit_result = submit_response.json()
            if not submit_result.get('success'):
                logging.error(f"Soumission échouée: {submit_result}")
                return None
                
            text_id = submit_result.get('data', {}).get('text', {}).get('id')
            if not text_id:
                logging.error("Pas d'ID de texte retourné")
                return None
                
            logging.info(f"✅ Texte soumis avec ID: {text_id}")
            
            # Étape 2: Attendre le traitement et récupérer les résultats
            result_url = f"https://plagiarismcheck.org/api/v1/text/{text_id}"
            
            for attempt in range(8):  # Max 8 tentatives
                logging.info(f"📊 Tentative {attempt+1}/8 - Récupération des résultats...")
                time.sleep(4)  # Attendre 4 secondes entre chaque tentative
                
                result_response = requests.get(result_url, headers={'X-API-TOKEN': token}, timeout=15)
                
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    text_data = result_data.get('data', {})
                    state = text_data.get('state', 0)
                    
                    if state == 4:  # Traitement terminé
                        # Récupérer les rapports de plagiat et IA
                        report_data = text_data.get('report')
                        ai_report_data = text_data.get('ai_report', {})
                        
                        plagiarism_percent = 0
                        sources_count = 0
                        ai_percent = 0
                        
                        # Traiter le rapport de plagiat
                        if report_data:
                            plagiarism_percent = report_data.get('percent', 0)
                            sources_count = len(report_data.get('sources', []))
                        
                        # Traiter le rapport IA
                        if ai_report_data and ai_report_data.get('status') == 4:
                            ai_percent = ai_report_data.get('percent', 0) or 0
                        
                        logging.info(f"🎯 PlagiarismCheck API résultat: {plagiarism_percent}% plagiat + {ai_percent}% IA")
                        
                        return {
                            'plagiarism': {
                                'percent': plagiarism_percent,
                                'sources_found': sources_count,
                                'details': report_data.get('sources', [])[:5] if report_data else []
                            },
                            'ai_content': {'percent': ai_percent},
                            'provider_used': 'plagiarismcheck_api_real',
                            'text_id': text_id
                        }
                    elif state == 3:  # En cours de traitement
                        # Vérifier si l'IA est déjà terminée
                        ai_report_data = text_data.get('ai_report', {})
                        if ai_report_data and ai_report_data.get('status') == 4:
                            ai_percent = ai_report_data.get('percent', 0) or 0
                            logging.info(f"⚡ IA terminée: {ai_percent}% - Plagiat en cours...")
                            
                            return {
                                'plagiarism': {'percent': 'En cours...', 'sources_found': 0},
                                'ai_content': {'percent': ai_percent},
                                'provider_used': 'plagiarismcheck_partial'
                            }
                        else:
                            logging.info(f"⏳ État: {state} - Traitement en cours...")
                            continue
                    elif state == 5:  # Traitement terminé avec rapport disponible
                        logging.info(f"État 5 détecté - Analyse terminée pour ID: {text_id}")
                        
                        # Récupérer les données de rapport (état 5 = traitement terminé dans ce contexte)
                        ai_report_data = text_data.get('ai_report', {})
                        report_data = text_data.get('report')
                        
                        plagiarism_percent = 0
                        sources_count = 0
                        ai_percent = 0
                        
                        # Traiter le rapport de plagiat
                        if report_data:
                            plagiarism_str = report_data.get('percent', '0')
                            plagiarism_percent = float(plagiarism_str) if plagiarism_str else 0
                            sources_count = report_data.get('source_count', 0)
                        
                        # Traiter le rapport IA (peut être null si pas encore traité)
                        if ai_report_data and ai_report_data.get('percent'):
                            ai_percent = float(ai_report_data.get('percent', 0))
                        
                        logging.info(f"🎯 PlagiarismCheck API état 5: {plagiarism_percent}% plagiat + {ai_percent}% IA")
                        
                        return {
                            'plagiarism': {
                                'percent': plagiarism_percent,
                                'sources_found': sources_count,
                                'details': []
                            },
                            'ai_content': {'percent': ai_percent},
                            'provider_used': 'plagiarismcheck_api_complete',
                            'text_id': text_id
                        }
                    else:
                        logging.info(f"⏳ État: {state} - Traitement en cours...")
                        continue
                else:
                    logging.error(f"Erreur récupération: {result_response.status_code}")
                    return None
            
            logging.warning("⏰ Timeout - Le traitement prend trop de temps")
            return None
                
        except Exception as e:
            logging.error(f"Erreur PlagiarismCheck: {e}")
            return None
    
    def _try_turnitin_local(self, text: str, filename: str) -> Optional[Dict]:
        """Essaie l'analyse avec l'algorithme local"""
        try:
            logging.info("Utilisation de l'algorithme local Turnitin-style")
            result = self.turnitin_local.detect_plagiarism(text)
            
            # Transformer au format standard avec détection IA
            response = {
                'plagiarism': result,
                'original_response': {
                    'method': 'turnitin_local_algorithm',
                    'analysis_details': result
                }
            }
            
            # Ajouter la détection IA si disponible
            if 'ai_percent' in result:
                response['ai_content'] = {
                    'percent': result['ai_percent'],
                    'detected': result.get('has_ai_content', False)
                }
            
            return response
            
        except Exception as e:
            logging.error(f"Erreur algorithme local: {e}")
            return None
    
    def _is_valid_result(self, result: Dict) -> bool:
        """Vérifie si un résultat est valide"""
        if not result:
            return False
        
        plagiarism = result.get('plagiarism', {})
        if not isinstance(plagiarism, dict):
            return False
        
        # Un résultat est valide s'il a au moins un pourcentage
        percent = plagiarism.get('percent')
        return percent is not None and isinstance(percent, (int, float)) and percent >= 0
    
    def get_service_status(self) -> Dict:
        """Retourne le statut de chaque service"""
        status = {}
        
        # Copyleaks
        copyleaks_available = bool(os.environ.get('COPYLEAKS_EMAIL') and os.environ.get('COPYLEAKS_API_KEY'))
        status['copyleaks'] = {
            'available': copyleaks_available,
            'priority': 1,
            'description': 'Service principal de détection'
        }
        
        # PlagiarismCheck
        plagiarismcheck_available = bool(os.environ.get('PLAGIARISMCHECK_API_TOKEN'))
        status['plagiarismcheck'] = {
            'available': plagiarismcheck_available,
            'priority': 2,
            'description': 'Service de fallback'
        }
        
        # Algorithme local
        status['turnitin_local'] = {
            'available': True,
            'priority': 3,
            'description': 'Algorithme local de dernier recours'
        }
        
        return status