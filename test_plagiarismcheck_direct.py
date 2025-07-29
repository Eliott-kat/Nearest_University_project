#!/usr/bin/env python3
"""
Test direct de l'API PlagiarismCheck avec vos vraies clés
"""
import os
import requests
import json
import time

def test_plagiarismcheck():
    """Test direct de PlagiarismCheck API"""
    api_url = "https://plagiarismcheck.org/api/v1/text"
    
    headers = {
        'X-API-TOKEN': os.environ.get('PLAGIARISMCHECK_API_TOKEN'),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'text': 'Au cours des dernières décennies, les avancées technologiques ont transformé notre quotidien. Des smartphones aux voitures autonomes, la technologie a modifié notre façon de communiquer.'
    }
    
    print(f"Testing PlagiarismCheck with token: {headers['X-API-TOKEN'][:10]}...")
    
    try:
        response = requests.post(api_url, headers=headers, data=data, timeout=15)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ PlagiarismCheck API fonctionne!")
            return result
        else:
            print(f"❌ Erreur: {response.status_code}")
            if response.status_code == 403:
                print("Erreur 403 - Token invalide ou quota dépassé")
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

if __name__ == "__main__":
    print("=== Test API PlagiarismCheck Directe ===")
    result = test_plagiarismcheck()
    if result:
        print(f"Résultat: {json.dumps(result, indent=2)}")
    print("=== Fin du test ===")