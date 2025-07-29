#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test simple pour vérifier l'installation locale
"""

print("🔬 Test d'installation AcadCheck")
print("=" * 40)

# Test 1 : Vérifier Python
import sys
print(f"✅ Python version: {sys.version}")

# Test 2 : Vérifier les modules essentiels
modules_required = [
    'flask', 'flask_sqlalchemy', 'sklearn', 
    'numpy', 'docx', 'PyPDF2', 'requests'
]

missing_modules = []
for module in modules_required:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError:
        print(f"❌ {module} - MANQUANT")
        missing_modules.append(module)

if missing_modules:
    print(f"\n⚠️ Modules manquants: {', '.join(missing_modules)}")
    print("\nInstallez avec:")
    print("pip install flask flask-sqlalchemy scikit-learn numpy python-docx PyPDF2 requests python-dotenv")
else:
    print("\n✅ Tous les modules requis sont installés!")

# Test 3 : Test algorithme simple
try:
    print("\n🧪 Test algorithme simple...")
    
    # Import du service unifié
    import os
    import sys
    sys.path.append('.')
    
    from unified_detection_service import UnifiedDetectionService
    
    # Test basique
    service = UnifiedDetectionService()
    test_text = "La biodiversité représente l'ensemble des espèces vivantes sur Terre."
    
    result = service.analyze_text(test_text, "test_local.txt")
    
    if result and 'plagiarism_score' in result:
        print(f"✅ Algorithme fonctionne: {result['plagiarism_score']:.1f}% plagiat, {result['ai_score']:.1f}% IA")
        print(f"   Service: {result.get('service_used', 'inconnu')}")
    else:
        print(f"❌ Problème algorithme: {result}")
        
except Exception as e:
    print(f"❌ Erreur test algorithme: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 40)
print("Test terminé!")