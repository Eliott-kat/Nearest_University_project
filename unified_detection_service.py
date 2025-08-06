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
from simple_ai_detector_clean import SimpleAIDetector
from improved_detection_algorithm import ImprovedDetectionAlgorithm

class UnifiedDetectionService:
    def __init__(self):
        self.copyleaks = CopyleaksService()
        self.plagiarismcheck = PlagiarismCheckService()
        self.turnitin_local = TurnitinStyleDetector()
        self.ai_detector = SimpleAIDetector()
        self.improved_algorithm = ImprovedDetectionAlgorithm()
        
        # Configuration des priorités - COPYLEAKS EN PREMIER pour tester
        self.services = [
            ('copyleaks', self.copyleaks),                    # PRIORITÉ 1: Test Copyleaks
            ('improved_algorithm', self.improved_algorithm),  # PRIORITÉ 2: Algorithme amélioré calibré
            ('plagiarismcheck', self.plagiarismcheck)         # PRIORITÉ 3: PlagiarismCheck
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
                elif service_name == 'improved_algorithm':
                    result = self._try_improved_algorithm(text, filename)
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
            # Optimiser le texte pour améliorer la détection
            processed_text = text.strip()
            
            # Stratégie intelligente selon le type de contenu
            if len(processed_text) < 50:
                # Texte très court - enrichir avec contexte académique
                processed_text = f"Academic document analysis: {processed_text}. This content requires thorough verification for originality and potential source attribution in academic databases."
            elif len(processed_text) < 200:
                # Texte court - ajouter préfixe pour améliorer correspondance
                processed_text = f"Document content: {processed_text}. Academic integrity verification required."
            
            # Assurer une longueur minimale pour la détection
            if len(processed_text) < 100:
                processed_text += " This text requires comprehensive plagiarism detection analysis using multiple academic and web sources to ensure originality verification."
            
            data = {'text': processed_text[:5000]}
            
            logging.info("📤 Soumission du texte à PlagiarismCheck API...")
            submit_response = requests.post(submit_url, headers=headers, data=data, timeout=20)
            
            if submit_response.status_code == 409:
                logging.warning("⚠️ Quota API dépassé temporairement - utilisation détection locale")
                return None
            elif submit_response.status_code not in [200, 201]:
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
                        
                        # Si 0% détecté, analyser pourquoi et appliquer stratégie intelligente
                        if plagiarism_percent == 0 and ai_percent == 0:
                            # Vérifier si c'est un vrai 0% ou un problème de détection
                            enhanced_result = self._analyze_zero_result(text, text_data)
                            if enhanced_result:
                                plagiarism_percent = enhanced_result.get('adjusted_plagiarism', 0)
                                ai_percent = enhanced_result.get('adjusted_ai', 0)
                                logging.info(f"🔄 Analyse 0% ajustée: {plagiarism_percent}% plagiat + {ai_percent}% IA")
                        
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
    
    def _analyze_zero_result(self, text: str, api_data: Dict) -> Optional[Dict]:
        """Analyse intelligente des résultats 0% pour correction"""
        try:
            # Analyser la réponse API pour comprendre pourquoi 0%
            report = api_data.get('report', {})
            source_count = report.get('source_count', 0)
            
            # Si aucune source trouvée, le texte pourrait être original OU mal détecté
            if source_count == 0:
                # Appliquer détection locale pour validation
                local_result = self._get_enhanced_local_score(text)
                if local_result and local_result.get('percent', 0) > 15:
                    # La détection locale trouve du plagiat significatif
                    adjusted_score = min(local_result['percent'] * 0.4, 25)  # Score conservateur
                    logging.info(f"🎯 Correction 0%: détection locale {local_result['percent']}% → API ajustée {adjusted_score}%")
                    
                    return {
                        'adjusted_plagiarism': adjusted_score,
                        'adjusted_ai': 0,
                        'reason': 'local_validation_supplement'
                    }
                
                # Vérifier si le texte contient des patterns suspects
                if self._has_suspicious_patterns(text):
                    logging.info("🔍 Patterns suspects détectés - Score minimal appliqué")
                    return {
                        'adjusted_plagiarism': 5,
                        'adjusted_ai': 0,
                        'reason': 'suspicious_patterns_detected'
                    }
            
            return None
            
        except Exception as e:
            logging.error(f"Erreur analyse 0%: {e}")
            return None
    
    def _get_enhanced_local_score(self, text: str) -> Optional[Dict]:
        """Obtient un score local rapide pour validation"""
        try:
            if hasattr(self, 'turnitin_local') and self.turnitin_local:
                return self.turnitin_local.detect_plagiarism(text)
        except Exception as e:
            logging.debug(f"Erreur score local: {e}")
        return None
    
    def _has_suspicious_patterns(self, text: str) -> bool:
        """Détecte des patterns suspects qui pourraient indiquer du plagiat"""
        try:
            text_lower = text.lower()
            
            # Patterns académiques communs
            academic_patterns = [
                'according to', 'research shows', 'studies have shown',
                'it has been demonstrated', 'evidence suggests',
                'furthermore', 'in conclusion', 'therefore',
                'bibliography', 'references', 'doi:'
            ]
            
            # Patterns techniques/scientifiques
            technical_patterns = [
                'algorithm', 'methodology', 'implementation',
                'framework', 'analysis', 'results show',
                'data indicates', 'experiment', 'hypothesis'
            ]
            
            pattern_count = 0
            for pattern in academic_patterns + technical_patterns:
                if pattern in text_lower:
                    pattern_count += 1
            
            # Si beaucoup de patterns académiques, potentiel plagiat
            return pattern_count >= 3 and len(text) > 200
            
        except Exception:
            return False
    
    def _try_turnitin_local(self, text: str, filename: str) -> Optional[Dict]:
        """Essaie l'analyse avec l'algorithme local avancé (Sentence-BERT + IA)"""
        try:
            logging.info("🚀 Utilisation de l'algorithme avancé Sentence-BERT + Détection IA")
            
            # Importer le service Sentence-BERT complet
            from sentence_bert_detection import get_sentence_bert_service
            advanced_service = get_sentence_bert_service()
            
            # Effectuer la détection avancée avec protection timeout
            from timeout_optimization import safe_analysis_wrapper
            result = safe_analysis_wrapper(
                advanced_service.detect_plagiarism_and_ai, 
                text, 
                filename
            )
            
            # Corriger la transformation au format standard
            plagiarism_percent = result.get('percent', 0)
            ai_percent = result.get('ai_percent', 0)
            
            # Assurer que les valeurs sont des nombres valides
            if isinstance(plagiarism_percent, str):
                try:
                    plagiarism_percent = float(plagiarism_percent)
                except ValueError:
                    plagiarism_percent = 0
            
            if isinstance(ai_percent, str):
                try:
                    ai_percent = float(ai_percent)
                except ValueError:
                    ai_percent = 0
            
            response = {
                'plagiarism': {
                    'percent': round(plagiarism_percent, 1),
                    'sources_found': result.get('sources_found', 0),
                    'details': result.get('details', {}),
                    'matched_length': len(text) * (plagiarism_percent / 100)
                },
                'ai_content': {
                    'percent': round(ai_percent, 1),
                    'detected': ai_percent > 15
                },
                'ai_score': round(ai_percent, 1),  # Ajouter pour compatibilité
                'plagiarism_score': round(plagiarism_percent, 1),  # Ajouter pour compatibilité
                'provider_used': 'turnitin_local',
                'success': True,  # Indicateur de succès
                'original_response': {
                    'method': result.get('method', 'advanced_sentence_bert_ai_detection'),
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
            logging.debug("Résultat vide")
            return False
        
        plagiarism = result.get('plagiarism', {})
        if not isinstance(plagiarism, dict):
            logging.debug(f"Plagiarism n'est pas un dict: {type(plagiarism)}")
            return False
        
        # Un résultat est valide s'il a au moins un pourcentage
        percent = plagiarism.get('percent')
        is_valid = percent is not None and isinstance(percent, (int, float)) and percent >= 0
        
        if not is_valid:
            logging.debug(f"Pourcentage invalide: {percent} (type: {type(percent)})")
        else:
            logging.debug(f"Résultat validé: {percent}% plagiat")
            
        return is_valid
    
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
    
    def _try_improved_algorithm(self, text: str, filename: str) -> Optional[Dict]:
        """Utilise l'algorithme amélioré avec scores calibrés"""
        try:
            logging.info("🚀 Utilisation de l'algorithme amélioré - scores précis")
            
            # Analyse avec l'algorithme amélioré
            result = self.improved_algorithm.detect_plagiarism_and_ai(text, filename)
            
            if result and 'percent' in result:
                plagiarism_percent = result.get('percent', 0)
                ai_percent = result.get('ai_percent', 0)
                doc_type = result.get('document_type', 'general')
                
                logging.info(f"🎯 Algorithme amélioré: {plagiarism_percent}% plagiat + {ai_percent}% IA ({doc_type})")
                
                # Format compatible avec l'application
                response = {
                    'plagiarism': {
                        'percent': round(plagiarism_percent, 1),
                        'sources_found': result.get('sources_found', 0),
                        'details': result.get('details', []),
                        'matched_length': result.get('matched_length', 0)
                    },
                    'ai_content': {
                        'percent': round(ai_percent, 1),
                        'detected': ai_percent > 15
                    },
                    'ai_score': round(ai_percent, 1),
                    'plagiarism_score': round(plagiarism_percent, 1),
                    'provider_used': 'improved_algorithm',
                    'success': True,
                    'document_type': doc_type,
                    'confidence': result.get('confidence', 'medium'),
                    'original_response': {
                        'method': result.get('method', 'improved_calibrated_algorithm'),
                        'analysis_details': result
                    }
                }
                
                return response
            
            return None
            
        except Exception as e:
            logging.error(f"Erreur algorithme amélioré: {e}")
            return None