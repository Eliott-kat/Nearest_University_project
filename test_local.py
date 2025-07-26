#!/usr/bin/env python3
"""
Script de test pour vérifier que l'application fonctionne
"""
import os
import requests
import time
import threading
from dotenv import load_dotenv

# Configuration
if os.path.exists('.env'):
    load_dotenv()

os.environ['DATABASE_URL'] = 'sqlite:///acadcheck.db'
os.makedirs('uploads', exist_ok=True)
os.makedirs('uploads/reports', exist_ok=True)

def start_app():
    """Démarre l'application Flask"""
    from app import app
    import routes  # Import routes to register them
    
    print("✅ Démarrage de l'application...")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def test_app():
    """Teste si l'application répond"""
    time.sleep(2)  # Attendre que l'app démarre
    
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        print(f"✅ Application accessible - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Page d'accueil fonctionne")
            
            # Test de la page d'upload
            response2 = requests.get('http://localhost:5000/upload', timeout=5)
            if response2.status_code == 200:
                print("✅ Page d'upload fonctionne")
            
            print("\n🎉 Application locale fonctionnelle !")
            print("📍 Accédez à: http://localhost:5000")
            
        else:
            print(f"❌ Erreur: Status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'application")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    # Démarrer l'app dans un thread séparé
    app_thread = threading.Thread(target=start_app, daemon=True)
    app_thread.start()
    
    # Tester l'application
    test_thread = threading.Thread(target=test_app)
    test_thread.start()
    test_thread.join()
    
    print("\nL'application continue de tourner...")
    try:
        app_thread.join()
    except KeyboardInterrupt:
        print("\n👋 Application arrêtée")