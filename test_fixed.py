#!/usr/bin/env python3
"""
Test de la version corrigée avec import routes
"""
import os
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

os.environ['DATABASE_URL'] = 'sqlite:///acadcheck.db'
os.makedirs('uploads', exist_ok=True)

# Simuler exactement ce que fait run_local.py maintenant
from app import app
import routes  # Import routes comme dans la version corrigée

print("🔍 Test de la configuration corrigée:")
print(f"✅ Routes enregistrées: {len(list(app.url_map.iter_rules()))}")

# Test avec le client de test Flask
with app.test_client() as client:
    response = client.get('/')
    print(f"✅ Status: {response.status_code}")
    
    if response.status_code == 200:
        print("🎉 La correction fonctionne ! Votre application devrait maintenant marcher.")
    else:
        print(f"❌ Problème persistant: {response.status_code}")
        
    # Test d'autres routes
    for path in ['/dashboard', '/upload', '/history']:
        resp = client.get(path)
        status = "✅" if resp.status_code == 200 else "❌"
        print(f"{status} {path}: {resp.status_code}")