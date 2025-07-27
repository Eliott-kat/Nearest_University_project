#!/usr/bin/env python3
"""
Test GPTZero integration with AcadCheck
"""
import os
import sys
from dotenv import load_dotenv
from gptzero_service_class import GPTZeroService

# Charger les variables d'environnement
load_dotenv()

def test_gptzero_configuration():
    """Test la configuration GPTZero"""
    print("🧪 Test de la configuration GPTZero")
    print("=" * 50)
    
    service = GPTZeroService()
    
    # Vérifier la configuration
    configured = service.is_configured()
    print(f"✅ GPTZero configuré: {configured}")
    
    if not configured:
        print("❌ GPTZERO_API_KEY non configuré dans .env")
        print("📋 Pour configurer GPTZero:")
        print("   1. Visitez: https://gptzero.me/pricing")
        print("   2. Choisissez le plan Premium ($16-24/mois)")
        print("   3. Obtenez votre clé: https://app.gptzero.me/app/api")
        print("   4. Ajoutez GPTZERO_API_KEY=votre-cle dans .env")
        return False
    
    # Test d'authentification
    print("\n🔐 Test d'authentification...")
    try:
        auth_success = service.authenticate()
        if auth_success:
            print("✅ Authentification GPTZero réussie")
            print("🎯 GPTZero disponible comme fallback")
        else:
            print("❌ Échec authentification GPTZero")
            print("💡 Vérifiez votre clé API dans .env")
            return False
    except Exception as e:
        print(f"❌ Erreur authentification: {str(e)}")
        return False
    
    return True

def test_gptzero_analysis():
    """Test une analyse simple avec GPTZero"""
    print("\n📊 Test d'analyse GPTZero")
    print("=" * 50)
    
    service = GPTZeroService()
    
    # Texte de test (contient probablement de l'IA)
    test_text = """
    Artificial intelligence has revolutionized the way we approach complex problems in various domains. 
    Machine learning algorithms can analyze vast amounts of data to identify patterns and make predictions with remarkable accuracy. 
    The integration of AI technologies in educational settings has opened new possibilities for personalized learning experiences.
    """
    
    print("📝 Analyse du texte de test...")
    print(f"Longueur: {len(test_text)} caractères")
    
    try:
        # Créer un objet document factice pour le test
        class MockDocument:
            def __init__(self):
                self.id = "test-doc"
                self.content = test_text
                self.copyleaks_id = None
        
        mock_doc = MockDocument()
        
        # Tester la soumission
        submission_id = service.submit_document(mock_doc)
        if submission_id:
            print(f"✅ Document soumis: {submission_id}")
            
            # Tester la récupération des résultats
            results = service.get_analysis_results(mock_doc)
            if results:
                print("✅ Résultats récupérés:")
                print(f"   - IA détectée: {results.get('ai_percentage', 0)}%")
                print(f"   - Plagiat: {results.get('plagiarism_percentage', 0)}%")
                print(f"   - Confiance: {results.get('confidence', 'N/A')}")
                print(f"   - Phrases suspectes: {len(results.get('highlighted_sentences', []))}")
                return True
            else:
                print("❌ Impossible de récupérer les résultats")
        else:
            print("❌ Échec de soumission du document")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {str(e)}")
        return False
    
    return False

def test_fallback_system():
    """Test du système de fallback avec GPTZero"""
    print("\n🔄 Test du système de fallback")
    print("=" * 50)
    
    try:
        from unified_plagiarism_service import UnifiedPlagiarismService
        
        service = UnifiedPlagiarismService()
        
        # Vérifier que GPTZero est dans la liste des services
        if hasattr(service, 'gptzero_service'):
            print("✅ GPTZero intégré dans le système unifié")
            
            # Tester l'ordre de fallback
            current_provider = service.get_current_provider_name()
            print(f"📍 Provider actuel: {current_provider}")
            print("🔄 Ordre de fallback: Copyleaks → PlagiarismCheck → GPTZero → Demo")
            
            return True
        else:
            print("❌ GPTZero non intégré dans le système unifié")
            
    except Exception as e:
        print(f"❌ Erreur test fallback: {str(e)}")
        
    return False

def main():
    """Fonction principale de test"""
    print("🚀 Test GPTZero pour AcadCheck")
    print("=" * 60)
    
    # Test 1: Configuration
    config_ok = test_gptzero_configuration()
    
    if config_ok:
        # Test 2: Analyse simple
        analysis_ok = test_gptzero_analysis()
        
        # Test 3: Système de fallback
        fallback_ok = test_fallback_system()
        
        print("\n" + "=" * 60)
        print("📋 RÉSUMÉ DES TESTS")
        print("=" * 60)
        print(f"✅ Configuration: {'OK' if config_ok else 'ÉCHEC'}")
        print(f"✅ Analyse: {'OK' if analysis_ok else 'ÉCHEC'}")
        print(f"✅ Fallback: {'OK' if fallback_ok else 'ÉCHEC'}")
        
        if config_ok and analysis_ok and fallback_ok:
            print("\n🎉 GPTZero prêt à utiliser comme fallback!")
            print("💡 Votre système a maintenant 3 APIs avant mode démo")
        else:
            print("\n⚠️  Quelques problèmes détectés, vérifiez la configuration")
    else:
        print("\n❌ Configuration GPTZero requise avant les tests avancés")

if __name__ == "__main__":
    main()