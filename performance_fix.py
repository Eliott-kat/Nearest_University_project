#!/usr/bin/env python3
"""
Corrections rapides de performance pour AcadCheck
"""

import os
import logging
import gc

def optimize_memory():
    """Optimise l'utilisation mémoire"""
    try:
        # Forcer le garbage collection
        collected = gc.collect()
        logging.info(f"🧹 Nettoyage mémoire: {collected} objets supprimés")
        
        # Réduire les caches
        import sys
        if hasattr(sys, 'intern'):
            sys.intern.clear()
        
        return True
    except Exception as e:
        logging.error(f"Erreur optimisation mémoire: {e}")
        return False

def disable_debug_features():
    """Désactive les fonctionnalités de debug pour améliorer les performances"""
    try:
        # Réduire le niveau de logging
        logging.getLogger().setLevel(logging.WARNING)
        
        # Désactiver les diagnostics verbose
        os.environ['DISABLE_VERBOSE_LOGGING'] = '1'
        
        logging.warning("🚀 Mode performance activé - logs réduits")
        return True
    except Exception as e:
        logging.error(f"Erreur désactivation debug: {e}")
        return False

def optimize_imports():
    """Optimise les imports pour réduire la charge"""
    try:
        # Supprimer les modules non utilisés du cache
        import sys
        modules_to_remove = []
        
        for module_name in sys.modules:
            if any(unused in module_name for unused in ['test_', 'debug_', 'enhanced_']):
                modules_to_remove.append(module_name)
        
        for module in modules_to_remove:
            if module in sys.modules:
                del sys.modules[module]
        
        logging.info(f"🧹 Modules non utilisés supprimés: {len(modules_to_remove)}")
        return True
    except Exception as e:
        logging.error(f"Erreur optimisation imports: {e}")
        return False

def quick_performance_boost():
    """Applique toutes les optimisations rapides"""
    results = []
    
    results.append(optimize_memory())
    results.append(disable_debug_features())
    results.append(optimize_imports())
    
    if all(results):
        logging.warning("✅ Optimisations performance appliquées avec succès")
    else:
        logging.error("⚠️ Certaines optimisations ont échoué")
    
    return all(results)

if __name__ == "__main__":
    quick_performance_boost()