#!/usr/bin/env python3
"""
Script de migration vers PlagiarismCheck API

Ce script vous aide à basculer de Copyleaks vers PlagiarismCheck en quelques étapes simples.
"""
import os
import sys

def show_instructions():
    """Afficher les instructions de migration"""
    print("🔄 Migration vers PlagiarismCheck API")
    print("=" * 50)
    
    print("\n📋 ÉTAPES DE MIGRATION:")
    print("\n1. Obtenez votre token PlagiarismCheck:")
    print("   • Visitez https://plagiarismcheck.org/")
    print("   • Créez un compte ou connectez-vous")
    print("   • Contactez le support pour obtenir votre API token")
    print("   • Copiez votre token (format: vsMKX3179tjK3CqvhE228IDeMV-eBBER)")
    
    print("\n2. Configurez votre fichier .env:")
    print("   • Ouvrez votre fichier .env")
    print("   • Ajoutez cette ligne:")
    print("     PLAGIARISMCHECK_API_TOKEN=votre-token-ici")
    print("   • Changez le provider:")
    print("     PLAGIARISM_API_PROVIDER=plagiarismcheck")
    
    print("\n3. Redémarrez l'application:")
    print("   • Arrêtez le serveur (Ctrl+C)")
    print("   • Relancez avec: python run_local.py")
    
    print("\n✅ AVANTAGES de PlagiarismCheck:")
    print("   • API plus stable que Copyleaks")
    print("   • Analyse rapide et précise")
    print("   • Intégration avec détection d'IA")
    print("   • Documentation claire")
    
    print("\n⚙️  EXEMPLE DE CONFIGURATION .env:")
    print("---")
    print("DATABASE_URL=sqlite:///acadcheck.db")
    print("SESSION_SECRET=ma-cle-secrete-super-longue-pour-acadcheck-2025")
    print("PLAGIARISM_API_PROVIDER=plagiarismcheck")
    print("PLAGIARISMCHECK_API_TOKEN=vsMKX3179tjK3CqvhE228IDeMV-eBBER")
    print("# Gardez aussi vos clés Copyleaks en fallback")
    print("COPYLEAKS_EMAIL=eliekatende35@gmail.com")
    print("COPYLEAKS_API_KEY=993b468e-6751-478e-9044-06e1a2fb8f75")
    print("---")
    
    print("\n🔗 RESSOURCES:")
    print("   • Documentation API: https://plagiarismcheck.org/for-developers/")
    print("   • Support: https://plagiarismcheck.org/contact-us/")
    
    print("\n⚠️  NOTES IMPORTANTES:")
    print("   • L'application basculera automatiquement en mode démonstration")
    print("   • si l'API PlagiarismCheck n'est pas accessible")
    print("   • Vous pouvez revenir à Copyleaks en changeant PLAGIARISM_API_PROVIDER=copyleaks")

def check_current_config():
    """Vérifier la configuration actuelle"""
    print("\n🔍 CONFIGURATION ACTUELLE:")
    print("-" * 30)
    
    current_provider = os.environ.get('PLAGIARISM_API_PROVIDER', 'copyleaks')
    print(f"Provider actuel: {current_provider}")
    
    copyleaks_configured = bool(os.environ.get('COPYLEAKS_EMAIL') and os.environ.get('COPYLEAKS_API_KEY'))
    plagiarismcheck_configured = bool(os.environ.get('PLAGIARISMCHECK_API_TOKEN'))
    
    print(f"Copyleaks configuré: {'✅' if copyleaks_configured else '❌'}")
    print(f"PlagiarismCheck configuré: {'✅' if plagiarismcheck_configured else '❌'}")
    
    if plagiarismcheck_configured and current_provider == 'copyleaks':
        print("\n💡 Vous pouvez basculer vers PlagiarismCheck!")
        print("   Changez PLAGIARISM_API_PROVIDER=plagiarismcheck dans .env")
    elif current_provider == 'plagiarismcheck' and plagiarismcheck_configured:
        print("\n✅ Vous utilisez déjà PlagiarismCheck!")
    elif current_provider == 'plagiarismcheck' and not plagiarismcheck_configured:
        print("\n⚠️  Provider PlagiarismCheck sélectionné mais token manquant")
        print("   Ajoutez PLAGIARISMCHECK_API_TOKEN dans .env")

if __name__ == "__main__":
    # Charger les variables d'environnement si possible
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    show_instructions()
    check_current_config()
    
    print("\n" + "=" * 50)
    print("🚀 Prêt à migrer ? Suivez les étapes ci-dessus !")