#!/usr/bin/env python3
"""
Test du système de fallback automatique entre APIs
"""
import os
import sys
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Add current directory to path for imports
sys.path.insert(0, '.')

def test_api_fallback():
    """Tester le mécanisme de fallback automatique"""
    print("🔄 TEST DU SYSTÈME DE FALLBACK AUTOMATIQUE")
    print("=" * 50)
    
    try:
        from simple_api_switch import get_active_service
        
        print("\n📋 CONFIGURATION ACTUELLE:")
        current_provider = os.environ.get('PLAGIARISM_API_PROVIDER', 'copyleaks')
        copyleaks_email = os.environ.get('COPYLEAKS_EMAIL', 'Non configuré')
        copyleaks_key = '***' if os.environ.get('COPYLEAKS_API_KEY') else 'Non configuré'
        plagiarismcheck_token = '***' if os.environ.get('PLAGIARISMCHECK_API_TOKEN') else 'Non configuré'
        
        print(f"Provider principal: {current_provider}")
        print(f"Copyleaks Email: {copyleaks_email}")
        print(f"Copyleaks API Key: {copyleaks_key}")
        print(f"PlagiarismCheck Token: {plagiarismcheck_token}")
        
        print("\n🔧 INITIALISATION DU SERVICE:")
        service = get_active_service()
        print(f"Service principal initialisé: {service._get_service_name(service._current_service)}")
        
        print("\n🔐 TEST D'AUTHENTIFICATION:")
        auth_result = service.authenticate()
        print(f"Résultat authentification: {'✅ Succès' if auth_result else '❌ Échec'}")
        
        if auth_result:
            print(f"Service actuel après auth: {service._get_service_name(service._current_service)}")
            print(f"Token disponible: {'✅ Oui' if service.token else '❌ Non'}")
        
        print("\n📊 ANALYSE DES SERVICES DISPONIBLES:")
        
        # Test Copyleaks
        copyleaks_configured = service._is_service_configured(service.copyleaks_service)
        print(f"Copyleaks configuré: {'✅' if copyleaks_configured else '❌'}")
        
        # Test PlagiarismCheck  
        plagiarismcheck_configured = service._is_service_configured(service.plagiarismcheck_service)
        print(f"PlagiarismCheck configuré: {'✅' if plagiarismcheck_configured else '❌'}")
        
        # Test fallback
        fallback_service = service._get_fallback_service()
        if fallback_service:
            print(f"Service de fallback: {service._get_service_name(fallback_service)}")
        else:
            print("Aucun service de fallback disponible")
        
        print("\n🎯 RECOMMANDATIONS:")
        
        if not copyleaks_configured and not plagiarismcheck_configured:
            print("⚠️  Aucune API configurée - seulement mode démonstration disponible")
            print("   Configurez au moins une API pour des résultats réels")
        elif copyleaks_configured and not plagiarismcheck_configured:
            print("💡 Copyleaks configuré, ajoutez PlagiarismCheck pour plus de redondance")
            print("   PLAGIARISMCHECK_API_TOKEN=votre-token-ici")
        elif not copyleaks_configured and plagiarismcheck_configured:
            print("💡 PlagiarismCheck configuré, ajoutez Copyleaks pour plus de redondance")
            print("   COPYLEAKS_EMAIL=votre@email.com")
            print("   COPYLEAKS_API_KEY=votre-cle-api")
        else:
            print("✅ Excellent ! Les deux APIs sont configurées")
            print("   Fallback automatique disponible en cas de panne")
        
        print("\n🚀 STATUT GLOBAL:")
        if auth_result:
            print("✅ Système prêt avec API réelle")
        elif copyleaks_configured or plagiarismcheck_configured:
            print("⚠️  APIs configurées mais indisponibles - basculement en mode démo")
        else:
            print("❌ Mode démonstration uniquement")
        
        return auth_result
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    # Charger les variables d'environnement si possible
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    test_api_fallback()
    
    print("\n" + "=" * 50)
    print("🔄 Test du fallback terminé !")