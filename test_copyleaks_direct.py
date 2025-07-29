#!/usr/bin/env python3
"""
Test direct de l'API Copyleaks avec vos vraies clés
"""
import os
import requests
import json
import time

def test_copyleaks_auth():
    """Test d'authentification Copyleaks"""
    auth_url = "https://id.copyleaks.com/v3/account/login"
    
    data = {
        'email': os.environ.get('COPYLEAKS_EMAIL'),
        'key': os.environ.get('COPYLEAKS_API_KEY')
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print(f"Testing auth with email: {data['email'][:10]}...")
    
    try:
        response = requests.post(auth_url, headers=headers, json=data, timeout=10)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            if token:
                print("✅ Authentification réussie!")
                return token
            else:
                print("❌ Pas de token dans la réponse")
                return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_copyleaks_submit(token, text):
    """Test de soumission d'un texte"""
    if not token:
        print("Pas de token, impossible de tester la soumission")
        return
    
    scan_id = f"test-{int(time.time())}"
    submit_url = f"https://api.copyleaks.com/v3/scans/submit/file/{scan_id}"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Encoder le texte en base64
    import base64
    base64_text = base64.b64encode(text.encode()).decode()
    
    data = {
        'base64': base64_text,
        'filename': 'test.txt',
        'properties': {
            'webhooks': {
                'status': 'https://httpbin.org/post/{STATUS}'
            }
        }
    }
    
    try:
        response = requests.post(submit_url, headers=headers, json=data, timeout=15)
        print(f"Submit status: {response.status_code}")
        print(f"Submit response: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            print("✅ Soumission réussie!")
            return scan_id
        else:
            print(f"❌ Erreur soumission: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur soumission: {e}")
        return None

if __name__ == "__main__":
    print("=== Test API Copyleaks Directe ===")
    
    # Test d'authentification
    token = test_copyleaks_auth()
    
    # Test de soumission si auth OK
    if token:
        test_text = "Au cours des dernières décennies, les avancées technologiques ont transformé notre quotidien."
        scan_id = test_copyleaks_submit(token, test_text)
        
        if scan_id:
            print(f"Scan ID créé: {scan_id}")
    
    print("=== Fin du test ===")