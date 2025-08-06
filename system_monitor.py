#!/usr/bin/env python3
"""
Système de surveillance en temps réel pour AcadCheck
Monitore les performances, erreurs et utilisation
"""

import psutil
import time
import threading
from datetime import datetime
import logging
from collections import defaultdict, deque

class SystemMonitor:
    """Moniteur système en temps réel"""
    
    def __init__(self):
        self.metrics = {
            'requests_count': 0,
            'upload_count': 0,
            'analysis_count': 0,
            'error_count': 0,
            'response_times': deque(maxlen=100),
            'memory_usage': deque(maxlen=60),  # 1 minute d'historique
            'cpu_usage': deque(maxlen=60),
            'disk_usage': 0,
            'active_users': set(),
            'popular_routes': defaultdict(int),
            'errors_by_type': defaultdict(int)
        }
        self.start_time = datetime.now()
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Démarre la surveillance"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logging.info("🟢 Surveillance système démarrée")
    
    def stop_monitoring(self):
        """Arrête la surveillance"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logging.info("🔴 Surveillance système arrêtée")
    
    def _monitor_loop(self):
        """Boucle de surveillance continue"""
        while self.monitoring:
            try:
                # Collecte des métriques système
                self.metrics['memory_usage'].append(psutil.virtual_memory().percent)
                self.metrics['cpu_usage'].append(psutil.cpu_percent())
                self.metrics['disk_usage'] = psutil.disk_usage('.').percent
                
                # Vérifie les seuils critiques
                self._check_critical_thresholds()
                
                time.sleep(10)  # Collecte toutes les 10 secondes (moins fréquent)
                
            except Exception as e:
                logging.error(f"Erreur surveillance: {e}")
                time.sleep(5)
    
    def _check_critical_thresholds(self):
        """Vérifie les seuils critiques"""
        # Mémoire critique (>85%) avec nettoyage automatique
        if self.metrics['memory_usage'] and self.metrics['memory_usage'][-1] > 85:
            try:
                import gc
                collected = gc.collect()
                logging.warning(f"⚠️ MÉMOIRE: {self.metrics['memory_usage'][-1]:.1f}% - Nettoyé {collected} objets")
            except Exception:
                logging.warning(f"⚠️ MÉMOIRE CRITIQUE: {self.metrics['memory_usage'][-1]:.1f}%")
        
        # CPU critique (>85%) avec limitation d'alertes
        if self.metrics['cpu_usage'] and self.metrics['cpu_usage'][-1] > 85:
            current_time = time.time()
            if not hasattr(self, '_last_cpu_warning'):
                self._last_cpu_warning = 0
            
            if current_time - self._last_cpu_warning > 30:  # Max 1 alerte par 30s
                logging.warning(f"⚠️ CPU ÉLEVÉ: {self.metrics['cpu_usage'][-1]:.1f}%")
                self._last_cpu_warning = current_time
        
        # Disque critique (>95%)
        if self.metrics['disk_usage'] > 95:
            logging.warning(f"⚠️ DISQUE CRITIQUE: {self.metrics['disk_usage']:.1f}%")
    
    def record_request(self, route, response_time, user_id=None):
        """Enregistre une requête"""
        self.metrics['requests_count'] += 1
        self.metrics['response_times'].append(response_time)
        self.metrics['popular_routes'][route] += 1
        
        if user_id:
            self.metrics['active_users'].add(user_id)
    
    def record_upload(self):
        """Enregistre un upload"""
        self.metrics['upload_count'] += 1
    
    def record_analysis(self):
        """Enregistre une analyse"""
        self.metrics['analysis_count'] += 1
    
    def record_error(self, error_type):
        """Enregistre une erreur"""
        self.metrics['error_count'] += 1
        self.metrics['errors_by_type'][error_type] += 1
    
    def get_status_report(self):
        """Génère un rapport de statut"""
        uptime = datetime.now() - self.start_time
        
        # Calculs des moyennes
        avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times']) if self.metrics['response_times'] else 0
        avg_memory = sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage']) if self.metrics['memory_usage'] else 0
        avg_cpu = sum(self.metrics['cpu_usage']) / len(self.metrics['cpu_usage']) if self.metrics['cpu_usage'] else 0
        
        # Top 3 routes populaires
        top_routes = sorted(self.metrics['popular_routes'].items(), key=lambda x: x[1], reverse=True)[:3]
        
        report = {
            'uptime': str(uptime).split('.')[0],  # Sans les microsecondes
            'status': self._get_overall_status(),
            'requests': {
                'total': self.metrics['requests_count'],
                'uploads': self.metrics['upload_count'],
                'analyses': self.metrics['analysis_count'],
                'errors': self.metrics['error_count'],
                'avg_response_time': f"{avg_response_time:.2f}ms"
            },
            'system': {
                'memory_usage': f"{avg_memory:.1f}%",
                'cpu_usage': f"{avg_cpu:.1f}%",
                'disk_usage': f"{self.metrics['disk_usage']:.1f}%"
            },
            'users': {
                'active_sessions': len(self.metrics['active_users'])
            },
            'popular_routes': [{'route': route, 'hits': hits} for route, hits in top_routes],
            'errors_by_type': dict(self.metrics['errors_by_type'])
        }
        
        return report
    
    def _get_overall_status(self):
        """Détermine le statut global du système"""
        if self.metrics['memory_usage'] and self.metrics['memory_usage'][-1] > 90:
            return 'CRITICAL'
        elif self.metrics['cpu_usage'] and self.metrics['cpu_usage'][-1] > 85:
            return 'WARNING'
        elif self.metrics['error_count'] > 10:
            return 'WARNING'
        else:
            return 'HEALTHY'

# Instance globale du moniteur
system_monitor = SystemMonitor()

# Décorateur pour monitorer les routes Flask
def monitor_route(route_name):
    """Décorateur pour monitorer une route Flask"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                response_time = (time.time() - start_time) * 1000  # en ms
                system_monitor.record_request(route_name, response_time)
                return result
            except Exception as e:
                system_monitor.record_error(type(e).__name__)
                raise
        return wrapper
    return decorator

def get_system_health():
    """Récupère la santé du système"""
    return system_monitor.get_status_report()

if __name__ == "__main__":
    # Test du moniteur
    print("🔍 TEST DU MONITEUR SYSTÈME")
    print("-" * 40)
    
    monitor = SystemMonitor()
    monitor.start_monitoring()
    
    # Simulation d'activité
    for i in range(5):
        monitor.record_request('/dashboard', 150 + i * 10)
        monitor.record_upload()
        if i % 2 == 0:
            monitor.record_analysis()
        time.sleep(0.1)
    
    # Rapport
    report = monitor.get_status_report()
    print("✅ Rapport de statut généré:")
    print(f"   - Statut: {report['status']}")
    print(f"   - Requêtes: {report['requests']['total']}")
    print(f"   - Temps de réponse moyen: {report['requests']['avg_response_time']}")
    print(f"   - Utilisation mémoire: {report['system']['memory_usage']}")
    
    monitor.stop_monitoring()
    print("✅ Test du moniteur terminé")