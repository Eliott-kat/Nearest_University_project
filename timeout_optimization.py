"""
Optimisation pour éviter les timeouts sur gros documents
"""
import signal
import logging
from typing import Dict, Any, Callable

class TimeoutOptimizer:
    """Gestionnaire de timeout pour éviter les blocages"""
    
    def __init__(self, max_seconds: int = 25):
        self.max_seconds = max_seconds
        self.original_handler = None
    
    def timeout_handler(self, signum, frame):
        """Handler appelé en cas de timeout"""
        raise TimeoutError(f"Opération interrompue après {self.max_seconds}s")
    
    def __enter__(self):
        """Démarrer le timeout"""
        self.original_handler = signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.max_seconds)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Arrêter le timeout"""
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
    """Wrapper sécurisé pour les analyses avec timeout"""
    try:
        # Optimiser le texte d'abord
        optimized_text = optimize_text_for_analysis(text)
        
        # Exécuter avec timeout
        with TimeoutOptimizer(25):  # 25 secondes max
            return analysis_func(optimized_text, *args, **kwargs)
    
    except TimeoutError:
        logging.warning("⏰ Timeout détecté - analyse simplifiée")
        return {
            'plagiarism_percentage': 0,
            'ai_probability': 0,
            'sources_found': 0,
            'method': 'timeout_fallback',
            'error': 'Document trop volumineux - analyse partielle'
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