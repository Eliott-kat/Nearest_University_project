#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script d'installation automatique des dépendances pour AcadCheck
"""

import subprocess
import sys
import os

def install_package(package):
    """Installe un package Python"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 Installation automatique d'AcadCheck")
    print("=" * 50)
    
    # Liste des dépendances essentielles
    dependencies = [
        "flask",
        "flask-sqlalchemy", 
        "flask-login",
        "python-docx",
        "PyPDF2",
        "requests",
        "python-dotenv",
        "werkzeug",
        "scikit-learn",
        "numpy",
        "nltk"
    ]
    
    # Dépendances optionnelles (peuvent échouer sans casser l'app)
    optional_dependencies = [
        "weasyprint",  # Pour les PDF (peut poser problème sur Windows)
        "psycopg2-binary",  # Pour PostgreSQL (optionnel en local)
        "flask-dance",  # Pour OAuth (optionnel en local)
        "pyjwt",  # Pour les tokens JWT
        "oauthlib",  # Pour OAuth
        "email-validator"  # Pour validation email
    ]
    
    print("Installation des dépendances essentielles...")
    failed_essential = []
    
    for package in dependencies:
        print(f"Installant {package}...")
        if install_package(package):
            print(f"✅ {package}")
        else:
            print(f"❌ {package} - ÉCHEC")
            failed_essential.append(package)
    
    print("\nInstallation des dépendances optionnelles...")
    failed_optional = []
    
    for package in optional_dependencies:
        print(f"Installant {package}...")
        if install_package(package):
            print(f"✅ {package}")
        else:
            print(f"⚠️ {package} - Échec (optionnel)")
            failed_optional.append(package)
    
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ D'INSTALLATION")
    print("=" * 50)
    
    if not failed_essential:
        print("✅ Toutes les dépendances essentielles installées !")
        print("🎯 AcadCheck devrait maintenant fonctionner correctement.")
        
        print("\n🚀 Pour lancer l'application :")
        print("python run_local.py")
        
    else:
        print("❌ Dépendances essentielles manquantes :")
        for pkg in failed_essential:
            print(f"   - {pkg}")
        print("\nInstallez-les manuellement avec :")
        print(f"pip install {' '.join(failed_essential)}")
    
    if failed_optional:
        print(f"\n⚠️ Dépendances optionnelles échouées : {', '.join(failed_optional)}")
        print("L'application fonctionnera sans elles (fonctionnalités limitées)")
    
    # Test final
    print("\n🧪 Test rapide de l'algorithme...")
    try:
        from unified_detection_service import UnifiedDetectionService
        service = UnifiedDetectionService()
        result = service.analyze_text("Test de fonctionnement de l'algorithme.", "test.txt")
        
        if result and 'plagiarism_score' in result:
            print(f"✅ Algorithme fonctionne ! Score test : {result['plagiarism_score']:.1f}%")
        else:
            print("⚠️ Algorithme ne retourne pas de résultat valide")
            
    except Exception as e:
        print(f"❌ Erreur test algorithme : {str(e)}")
        print("Vérifiez que toutes les dépendances sont installées")

if __name__ == "__main__":
    main()