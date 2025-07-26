#!/usr/bin/env python3
"""
Script de lancement pour installation locale d'AcadCheck
"""
import os
from dotenv import load_dotenv

# Charger le fichier .env s'il existe
if os.path.exists('.env'):
    load_dotenv()
    print("✓ Fichier .env chargé")
else:
    print("! Fichier .env non trouvé, utilisation des valeurs par défaut")

# Configuration par défaut pour installation locale
# Forcer SQLite pour éviter les problèmes de connexion PostgreSQL
os.environ['DATABASE_URL'] = 'sqlite:///acadcheck.db'
os.environ.setdefault('SESSION_SECRET', 'ma-cle-secrete-super-longue-pour-acadcheck-2025')

# Vérifier si les clés Copyleaks sont configurées
copyleaks_email = os.environ.get('COPYLEAKS_EMAIL')
copyleaks_key = os.environ.get('COPYLEAKS_API_KEY')

if copyleaks_email and copyleaks_key:
    print(f"✓ API Copyleaks configurée avec: {copyleaks_email}")
else:
    print("! API Copyleaks non configurée - mode démonstration activé")

# Créer les dossiers nécessaires
os.makedirs('uploads', exist_ok=True)
os.makedirs('uploads/reports', exist_ok=True)
print("✓ Dossiers créés")

# Lancer l'application
if __name__ == "__main__":
    from app import app
    import routes  # IMPORTANT: Import routes to register them
    
    print("🚀 Lancement d'AcadCheck...")
    print("📍 Application disponible sur: http://localhost:5000")
    
    if os.environ.get('NGROK_URL'):
        print(f"🌐 URL publique (ngrok): {os.environ.get('NGROK_URL')}")
    
    # Vérifier que les routes sont bien enregistrées
    print(f"Routes disponibles: {len(list(app.url_map.iter_rules()))} routes")
    
    app.run(host="0.0.0.0", port=5000, debug=True)