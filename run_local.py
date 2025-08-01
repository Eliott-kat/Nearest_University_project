#!/usr/bin/env python3
"""
Script de lancement local pour AcadCheck
Utilise SQLite au lieu de PostgreSQL pour un déploiement local simple
"""

import os
import sys
from pathlib import Path

def setup_local_environment():
    """Configure l'environnement pour une exécution locale"""
    print("🔧 Configuration de l'environnement local...")
    
    # Configuration des variables d'environnement pour local
    os.environ['DATABASE_URL'] = 'sqlite:///instance/acadcheck_local.db'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    # Clé secrète pour le développement local
    if not os.environ.get('FLASK_SECRET_KEY'):
        os.environ['FLASK_SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # Créer les dossiers nécessaires
    folders = ['instance', 'uploads', 'plagiarism_cache', 'report_screenshots']
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
    
    print("✅ Environnement configuré")

def check_dependencies():
    """Vérifie que les dépendances principales sont installées"""
    print("🔍 Vérification des dépendances...")
    
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf',
        'werkzeug', 'requests', 'pypdf2', 'docx', 'scikit_learn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('_', '.') if '_' in package else package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Packages manquants: {', '.join(missing_packages)}")
        print("\n💡 Pour installer les dépendances:")
        print("pip install flask flask-sqlalchemy flask-login flask-wtf")
        print("pip install werkzeug requests pypdf2 python-docx")
        print("pip install scikit-learn numpy weasyprint")
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def initialize_database():
    """Initialise la base de données locale"""
    print("🗄️ Initialisation de la base de données...")
    
    try:
        from app import app, db
        
        with app.app_context():
            # Créer toutes les tables
            db.create_all()
            print("✅ Base de données initialisée")
            
            # Vérifier la connexion
            from models import User
            user_count = db.session.query(User).count()
            print(f"📊 Utilisateurs dans la base: {user_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la DB: {e}")
        return False

def run_application():
    """Lance l'application Flask"""
    print("🚀 Lancement de l'application AcadCheck...")
    
    try:
        from app import app
        
        # Configuration pour le mode local
        app.config['DEBUG'] = True
        app.config['TESTING'] = False
        
        print("\n" + "="*50)
        print("🎯 AcadCheck - Mode Local")
        print("="*50)
        print("📍 URL: http://localhost:5000")
        print("🔧 Mode: Développement")
        print("🗄️ Base de données: SQLite locale")
        print("🛡️ Authentification: Système simplifié")
        print("="*50)
        print("\nAppuyez sur Ctrl+C pour arrêter l'application")
        print("")
        
        # Lancer le serveur de développement
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Application arrêtée par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        sys.exit(1)

def main():
    """Fonction principale"""
    print("\n🎓 AcadCheck - Installation Locale")
    print("=" * 40)
    
    # Étape 1: Configuration de l'environnement
    setup_local_environment()
    
    # Étape 2: Vérification des dépendances
    if not check_dependencies():
        print("\n🔴 Installation interrompue - dépendances manquantes")
        sys.exit(1)
    
    # Étape 3: Initialisation de la base de données
    if not initialize_database():
        print("\n🔴 Installation interrompue - problème de base de données")
        sys.exit(1)
    
    # Étape 4: Lancement de l'application
    run_application()

if __name__ == '__main__':
    main()