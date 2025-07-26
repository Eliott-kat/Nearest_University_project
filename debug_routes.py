#!/usr/bin/env python3
"""
Script de debug pour vérifier les routes
"""
import os
from dotenv import load_dotenv

# Configuration
if os.path.exists('.env'):
    load_dotenv()

os.environ['DATABASE_URL'] = 'sqlite:///acadcheck.db'
os.makedirs('uploads', exist_ok=True)

# Test des imports
try:
    from app import app
    print("✅ app.py importé avec succès")
    
    import routes
    print("✅ routes.py importé avec succès")
    
    # Vérifier les routes
    with app.app_context():
        rules = list(app.url_map.iter_rules())
        print(f"\n📍 {len(rules)} routes trouvées:")
        for rule in rules:
            print(f"  {rule.rule} -> {rule.endpoint}")
    
    # Test de la route principale
    with app.test_client() as client:
        response = client.get('/')
        print(f"\n🌐 Test de la route principale:")
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.content_type}")
        print(f"  Taille: {len(response.data)} bytes")
        
        if response.status_code != 200:
            print(f"❌ Erreur: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)[:200]}...")
        else:
            print("✅ Route principale fonctionne!")

except Exception as e:
    print(f"❌ Erreur d'import: {e}")
    import traceback
    traceback.print_exc()