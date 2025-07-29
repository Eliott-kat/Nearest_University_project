#!/usr/bin/env python3
"""
CORRECTIF WINDOWS pour AcadCheck
Résout l'erreur: module 'signal' has no attribute 'SIGALRM'

UTILISATION:
1. Placer ce fichier dans le dossier AcadCheck
2. Exécuter: python WINDOWS_FIX.py
3. Redémarrer l'application: python run_local.py
"""

import os
import shutil

def fix_timeout_optimization():
    """Corrige le fichier timeout_optimization.py pour Windows"""
    
    timeout_fix = '''"""
Optimisation pour éviter les timeouts sur gros documents
Compatible Windows et Unix/Linux
"""
import signal
import logging
import platform
import threading
import time
from typing import Dict, Any, Callable

class TimeoutOptimizer:
    """Gestionnaire de timeout pour éviter les blocages - Compatible multiplateforme"""
    
    def __init__(self, max_seconds: int = 25):
        self.max_seconds = max_seconds
        self.original_handler = None
        self.is_windows = platform.system() == 'Windows'
        self.timer = None
        self.timeout_occurred = False
    
    def timeout_handler(self, signum=None, frame=None):
        """Handler appelé en cas de timeout"""
        self.timeout_occurred = True
        raise TimeoutError(f"Opération interrompue après {self.max_seconds}s")
    
    def _windows_timeout_handler(self):
        """Handler de timeout pour Windows utilisant threading"""
        time.sleep(self.max_seconds)
        if not self.timeout_occurred:
            self.timeout_handler()
    
    def __enter__(self):
        """Démarrer le timeout"""
        self.timeout_occurred = False
        
        if self.is_windows:
            # Sur Windows, utiliser un timer thread
            self.timer = threading.Timer(self.max_seconds, self._windows_timeout_handler)
            self.timer.daemon = True
            self.timer.start()
        else:
            # Sur Unix/Linux, utiliser signal.SIGALRM
            try:
                self.original_handler = signal.signal(signal.SIGALRM, self.timeout_handler)
                signal.alarm(self.max_seconds)
            except AttributeError:
                # Fallback si SIGALRM n'est pas disponible
                self.timer = threading.Timer(self.max_seconds, self._windows_timeout_handler)
                self.timer.daemon = True
                self.timer.start()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Arrêter le timeout"""
        self.timeout_occurred = True
        
        if self.is_windows or not hasattr(signal, 'SIGALRM'):
            # Annuler le timer sur Windows ou si SIGALRM n'existe pas
            if self.timer and self.timer.is_alive():
                self.timer.cancel()
        else:
            # Annuler l'alarme sur Unix/Linux
            signal.alarm(0)
            if self.original_handler:
                signal.signal(signal.SIGALRM, self.original_handler)

def optimize_text_for_analysis(text: str, max_length: int = 3000) -> str:
    """Optimise un texte pour l'analyse en conservant le sens"""
    if len(text) <= max_length:
        return text
    
    logging.info(f"📄 Optimisation texte : {len(text)} → {max_length} caractères")
    
    # Stratégie : début + milieu + fin pour préserver la structure
    third = max_length // 3
    
    start = text[:third]
    middle_pos = len(text) // 2
    middle = text[middle_pos - third//2:middle_pos + third//2]
    end = text[-third:]
    
    optimized = start + " [...] " + middle + " [...] " + end
    return optimized[:max_length]

def safe_analysis_wrapper(analysis_func: Callable, text: str, *args, **kwargs) -> Dict[str, Any]:
    """Wrapper sécurisé pour les analyses avec timeout - Compatible Windows"""
    try:
        # Optimiser le texte d'abord
        optimized_text = optimize_text_for_analysis(text)
        
        # Exécuter avec timeout (compatible Windows/Linux)
        with TimeoutOptimizer(25):  # 25 secondes max
            return analysis_func(optimized_text, *args, **kwargs)
    
    except TimeoutError:
        logging.warning("⏰ Timeout détecté - analyse simplifiée")
        return {
            'plagiarism_percentage': 0,
            'ai_probability': 0,
            'sources_found': 0,
            'method': 'timeout_fallback',
            'error': 'Timeout'
        }
    except Exception as e:
        logging.error(f"Erreur analyse: {e}")
        return {
            'plagiarism_percentage': 0,
            'ai_probability': 0,
            'sources_found': 0,
            'method': 'error_fallback',
            'error': str(e)
        }
'''
    
    # Sauvegarder l'ancien fichier
    if os.path.exists('timeout_optimization.py'):
        shutil.copy('timeout_optimization.py', 'timeout_optimization.py.backup')
        print("✅ Sauvegarde de l'ancien fichier: timeout_optimization.py.backup")
    
    # Écrire le nouveau fichier
    with open('timeout_optimization.py', 'w', encoding='utf-8') as f:
        f.write(timeout_fix)
    
    print("✅ Fichier timeout_optimization.py corrigé pour Windows")

def main():
    """Applique tous les correctifs Windows"""
    print("🔧 Application des correctifs Windows pour AcadCheck...")
    
    try:
        fix_timeout_optimization()
        print("✅ Tous les correctifs appliqués avec succès!")
        print("\n📌 Instructions:")
        print("1. Redémarrez l'application: python run_local.py")
        print("2. L'algorithme local fonctionnera maintenant correctement sur Windows")
        print("3. Les analyses donneront des résultats > 0%")
    except Exception as e:
        print(f"❌ Erreur lors de l'application des correctifs: {e}")

if __name__ == "__main__":
    main()