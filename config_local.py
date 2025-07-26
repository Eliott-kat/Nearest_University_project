import os
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

class Config:
    """Configuration locale pour AcadCheck"""
    
    # Base de données SQLite locale (plus simple)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///acadcheck.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Sécurité
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # Configuration Copyleaks
    COPYLEAKS_EMAIL = os.environ.get('COPYLEAKS_EMAIL')
    COPYLEAKS_API_KEY = os.environ.get('COPYLEAKS_API_KEY')
    
    # URL de base pour les webhooks
    BASE_URL = os.environ.get('NGROK_URL', 'http://localhost:5000')
    
    # Configuration de upload
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size