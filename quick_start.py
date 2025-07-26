#!/usr/bin/env python3
"""
Démarrage rapide d'AcadCheck avec vos vraies clés API
"""
import os
import webbrowser
import time
from dotenv import load_dotenv

# Configuration
if os.path.exists('.env'):
    load_dotenv()
    print("✅ Fichier .env chargé")

# Forcer SQLite 
os.environ['DATABASE_URL'] = 'sqlite:///acadcheck.db'
os.makedirs('uploads', exist_ok=True)
os.makedirs('uploads/reports', exist_ok=True)

# Vérifier les clés API
copyleaks_email = os.environ.get('COPYLEAKS_EMAIL')
if copyleaks_email:
    print(f"✅ API Copyleaks: {copyleaks_email}")
else:
    print("⚠️  Mode démonstration - API Copyleaks non configurée")

ngrok_url = os.environ.get('NGROK_URL')
if ngrok_url:
    print(f"🌐 URL ngrok: {ngrok_url}")

# Démarrer l'application
print("\n🚀 Démarrage d'AcadCheck...")
print("📍 Local: http://localhost:5000")

# Ouvrir automatiquement le navigateur après 2 secondes
def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

import threading
threading.Thread(target=open_browser, daemon=True).start()

# Lancer l'app
from app import app
import routes  # Import routes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)