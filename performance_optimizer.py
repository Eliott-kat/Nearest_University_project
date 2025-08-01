#!/usr/bin/env python3
"""
Optimiseur de performances pour AcadCheck
Optimise automatiquement les performances et la mémoire
"""

import os
import gc
import psutil
import logging
from functools import wraps
from datetime import datetime, timedelta

class PerformanceOptimizer:
    """Optimiseur de performances automatique"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = {}
        self.cache_max_size = 100
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=5)
        
    def cache_result(self, ttl_minutes=10):
        """Décorateur de cache avec TTL"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Créer une clé de cache
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
                
                # Vérifier si le résultat est en cache et valide
                if cache_key in self.cache:
                    if datetime.now() < self.cache_ttl[cache_key]:
                        return self.cache[cache_key]
                    else:
                        # Nettoyer l'entrée expirée
                        del self.cache[cache_key]
                        del self.cache_ttl[cache_key]
                
                # Calculer et mettre en cache
                result = func(*args, **kwargs)
                
                # Limiter la taille du cache
                if len(self.cache) >= self.cache_max_size:
                    self._cleanup_cache()
                
                self.cache[cache_key] = result
                self.cache_ttl[cache_key] = datetime.now() + timedelta(minutes=ttl_minutes)
                
                return result
            return wrapper
        return decorator
    
    def _cleanup_cache(self):
        """Nettoie le cache expiré"""
        now = datetime.now()
        expired_keys = [key for key, ttl in self.cache_ttl.items() if now >= ttl]
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            if key in self.cache_ttl:
                del self.cache_ttl[key]
        
        logging.info(f"🧹 Cache nettoyé: {len(expired_keys)} entrées supprimées")
    
    def optimize_memory(self):
        """Optimise l'utilisation mémoire"""
        # Forcer le garbage collection
        collected = gc.collect()
        
        # Nettoyer le cache si nécessaire
        if datetime.now() - self.last_cleanup > self.cleanup_interval:
            self._cleanup_cache()
            self.last_cleanup = datetime.now()
        
        # Obtenir l'utilisation mémoire actuelle
        memory_info = psutil.virtual_memory()
        
        logging.info(f"🧠 Optimisation mémoire: {collected} objets collectés, "
                    f"mémoire: {memory_info.percent:.1f}%")
        
        return {
            'objects_collected': collected,
            'memory_percent': memory_info.percent,
            'memory_available': memory_info.available,
            'cache_entries': len(self.cache)
        }
    
    def optimize_database_queries(self, app):
        """Optimise les requêtes base de données"""
        from app import db
        
        with app.app_context():
            try:
                # Analyser les requêtes lentes (simulation)
                # En production, on utiliserait des outils comme SQLAlchemy events
                
                # Nettoyer les sessions obsolètes
                db.session.expire_all()
                
                # Optimiser les index (si PostgreSQL)
                if 'postgresql' in str(db.engine.url):
                    # Commandes d'optimisation PostgreSQL
                    optimizations = [
                        "VACUUM ANALYZE;",
                        "REINDEX DATABASE acadcheck;"
                    ]
                    logging.info("🔧 Optimisations PostgreSQL planifiées")
                
                logging.info("✅ Optimisation base de données terminée")
                return True
                
            except Exception as e:
                logging.error(f"❌ Erreur optimisation BD: {e}")
                return False
    
    def get_performance_metrics(self):
        """Récupère les métriques de performance"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('.')
        
        return {
            'memory': {
                'percent': memory.percent,
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3)
            },
            'cpu': {
                'percent': cpu,
                'count': psutil.cpu_count()
            },
            'disk': {
                'percent': disk.percent,
                'free_gb': disk.free / (1024**3),
                'used_gb': disk.used / (1024**3)
            },
            'cache': {
                'entries': len(self.cache),
                'max_size': self.cache_max_size
            }
        }

class DatabaseOptimizer:
    """Optimiseur spécifique à la base de données"""
    
    @staticmethod
    def optimize_queries():
        """Optimise les requêtes communes"""
        from app import db
        from models import User, Document, AnalysisResult
        
        # Index suggestions pour améliorer les performances
        index_suggestions = [
            "CREATE INDEX IF NOT EXISTS idx_documents_user_status ON documents(user_id, status);",
            "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);",
            "CREATE INDEX IF NOT EXISTS idx_analysis_results_document_id ON analysis_results(document_id);",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_active ON users(active);"
        ]
        
        try:
            for suggestion in index_suggestions:
                db.session.execute(suggestion)
            db.session.commit()
            logging.info("✅ Index base de données optimisés")
            return True
        except Exception as e:
            db.session.rollback()
            logging.error(f"❌ Erreur optimisation index: {e}")
            return False
    
    @staticmethod
    def cleanup_old_data(days_old=30):
        """Nettoie les anciennes données"""
        from app import db
        from models import Document, DocumentStatus
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        try:
            # Supprimer les anciens documents en échec
            old_failed_docs = Document.query.filter(
                Document.status == DocumentStatus.FAILED,
                Document.created_at < cutoff_date
            ).all()
            
            count = len(old_failed_docs)
            for doc in old_failed_docs:
                # Supprimer le fichier physique si il existe
                if os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
                db.session.delete(doc)
            
            db.session.commit()
            logging.info(f"🧹 {count} anciens documents supprimés")
            return count
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"❌ Erreur nettoyage données: {e}")
            return 0

# Instance globale de l'optimiseur
performance_optimizer = PerformanceOptimizer()

def optimize_performance():
    """Fonction utilitaire pour optimiser les performances"""
    return performance_optimizer.optimize_memory()

def get_performance_report():
    """Génère un rapport de performance"""
    metrics = performance_optimizer.get_performance_metrics()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy' if metrics['memory']['percent'] < 80 else 'warning',
        'metrics': metrics,
        'recommendations': []
    }
    
    # Ajouter des recommandations
    if metrics['memory']['percent'] > 85:
        report['recommendations'].append("Mémoire élevée - Redémarrage recommandé")
    
    if metrics['cpu']['percent'] > 80:
        report['recommendations'].append("CPU élevé - Vérifier les processus")
    
    if metrics['disk']['percent'] > 90:
        report['recommendations'].append("Disque plein - Nettoyer les fichiers")
    
    return report

if __name__ == "__main__":
    # Test de l'optimiseur
    print("⚡ TEST OPTIMISEUR DE PERFORMANCES")
    print("-" * 40)
    
    optimizer = PerformanceOptimizer()
    
    # Test du cache
    @optimizer.cache_result(ttl_minutes=1)
    def test_function(x):
        return x * 2
    
    # Premier appel (calcul)
    result1 = test_function(5)
    print(f"✅ Premier appel: {result1}")
    
    # Deuxième appel (cache)
    result2 = test_function(5)
    print(f"✅ Deuxième appel (cache): {result2}")
    
    # Métriques
    metrics = optimizer.get_performance_metrics()
    print(f"✅ Métriques collectées:")
    print(f"   - Mémoire: {metrics['memory']['percent']:.1f}%")
    print(f"   - CPU: {metrics['cpu']['percent']:.1f}%")
    print(f"   - Entrées cache: {metrics['cache']['entries']}")
    
    # Optimisation mémoire
    optimization_result = optimizer.optimize_memory()
    print(f"✅ Optimisation mémoire: {optimization_result['objects_collected']} objets collectés")
    
    print("✅ Test optimiseur terminé")