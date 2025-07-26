#!/usr/bin/env python3
"""
Test de l'état actuel de l'API Copyleaks
"""
import requests
import json
import os
from datetime import datetime

def test_copyleaks_status():
    """Test direct de l'API Copyleaks"""
    
    email = "eliekatende35@gmail.com"
    api_key = "993b468e-6751-478e-9044-06e1a2fb8f75"
    
    print(f"🔍 Test de l'API Copyleaks - {datetime.now().strftime('%H:%M:%S')}")
    print(f"📧 Email: {email}")
    
    auth_url = "https://id.copyleaks.com/v3/account/login"
    headers = {'Content-Type': 'application/json'}
    data = {'email': email, 'key': api_key}
    
    try:
        response = requests.post(auth_url, headers=headers, json=data, timeout=10)
        
        print(f"\n📊 Résultat:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('access_token'):
                print("✅ API Copyleaks fonctionnelle - Token reçu")
                print(f"Token (extrait): {result['access_token'][:20]}...")
            else:
                print("⚠️  Réponse reçue mais pas de token")
                print(f"Contenu: {response.text[:200]}")
                
        elif response.status_code == 500:
            print("❌ Erreur 500 - Problème serveur Copyleaks")
            print("   → Ce n'est PAS un problème de vos identifiants")
            print("   → Le serveur Copyleaks est temporairement indisponible")
            
        elif response.status_code == 401:
            print("❌ Erreur 401 - Identifiants invalides")
            print("   → Vérifiez votre email et clé API")
            
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Contenu: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - Serveur Copyleaks ne répond pas")
        
    except requests.exceptions.ConnectionError:
        print("🌐 Erreur de connexion - Problème réseau ou serveur indisponible")
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    test_copyleaks_status()