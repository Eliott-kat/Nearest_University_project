"""
Configuration locale pour AcadCheck
Copiez ce fichier et renommez-le en config.py pour votre installation locale
"""
import os

# Variables d'environnement pour installation locale
def setup_local_environment():
    """Configure les variables d'environnement pour l'installation locale"""
    os.environ.setdefault('DATABASE_URL', 'sqlite:///acadcheck.db')
    os.environ.setdefault('SESSION_SECRET', 'ma-cle-secrete-super-longue-pour-acadcheck-2025')
    os.environ.setdefault('COPYLEAKS_EMAIL', 'demo@acadcheck.local')
    os.environ.setdefault('COPYLEAKS_API_KEY', 'demo-key')
    os.environ.setdefault('REPL_ID', 'acadcheck-local')

# Appeler automatiquement au import
setup_local_environment()