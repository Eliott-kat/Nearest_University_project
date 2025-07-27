#!/usr/bin/env python3
"""
Test du système de fallback simplifié : Copyleaks → GPTZero
"""
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_simplified_fallback():
    """Test le système de fallback simplifié"""
    print("🔄 Test du système de fallback simplifié")
    print("=" * 50)
    
    try:
        from unified_plagiarism_service import UnifiedPlagiarismService
        
        service = UnifiedPlagiarismService()
        
        print("✅ Service unifié initialisé")
        print("📋 Configuration actuelle :")
        print("   - Service principal : Copyleaks")
        print("   - Fallback : GPTZero")
        print("   - Mode démo : si tous échouent")
        
        # Vérifier les services disponibles
        copyleaks_configured = bool(service.copyleaks_service.email and service.copyleaks_service.api_key)
        gptzero_configured = service.gptzero_service.is_configured()
        
        print(f"\n🔧 État des services :")
        print(f"   - Copyleaks : {'✅ OK' if copyleaks_configured else '❌ Non configuré'}")
        print(f"   - GPTZero : {'✅ OK' if gptzero_configured else '❌ Non configuré'}")
        
        # Test d'authentification
        print(f"\n🔐 Test d'authentification...")
        auth_success = service.authenticate()
        
        if auth_success:
            current_provider = service.get_current_provider_name()
            print(f"✅ Authentification réussie avec : {current_provider}")
        else:
            print("❌ Échec d'authentification sur tous les services")
            print("💡 Mode démonstration sera utilisé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test : {str(e)}")
        return False

def show_configuration_guide():
    """Affiche le guide de configuration"""
    print("\n📋 GUIDE DE CONFIGURATION")
    print("=" * 50)
    
    print("Pour utiliser le système complet, configurez dans votre .env :")
    print()
    print("# Copyleaks (service principal)")
    print("COPYLEAKS_EMAIL=votre-email@copyleaks.com")
    print("COPYLEAKS_API_KEY=votre-cle-copyleaks")
    print()
    print("# GPTZero (fallback)")
    print("GPTZERO_API_KEY=gpt_votre_cle_gptzero")
    print()
    print("🔗 Pour obtenir les clés :")
    print("   - Copyleaks : https://copyleaks.com/")
    print("   - GPTZero : https://gptzero.me/pricing (Plan Premium)")

def main():
    """Fonction principale"""
    print("🚀 Test du système de fallback simplifié")
    print("📍 Copyleaks → GPTZero → Mode démo")
    print("=" * 60)
    
    # Test du système
    test_ok = test_simplified_fallback()
    
    if test_ok:
        print("\n✅ Système de fallback simplifié fonctionnel")
        print("🎯 Ordre : Copyleaks → GPTZero → Démonstration")
        
        # Guide de configuration
        show_configuration_guide()
    else:
        print("\n❌ Problème détecté dans le système")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()