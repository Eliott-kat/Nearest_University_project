#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Débogage du processus de traitement des résultats
"""

import sys
sys.path.append('.')

from unified_detection_service import UnifiedDetectionService

def debug_result_processing():
    print("🔬 Débogage traitement des résultats")
    print("=" * 50)
    
    # Texte de test
    test_text = "La biodiversité est l'ensemble des êtres vivants ainsi que les écosystèmes dans lesquels ils évoluent."
    
    # 1. Test du service unifié
    unified_service = UnifiedDetectionService()
    result = unified_service.analyze_text(test_text, "debug_test.txt")
    
    print(f"Résultat brut: {result}")
    print()
    
    if result:
        print("Structure des résultats:")
        print(f"- Type: {type(result)}")
        print(f"- Clés disponibles: {result.keys()}")
        print()
        
        # Vérifier la structure plagiarism
        plagiarism = result.get('plagiarism', {})
        print(f"Plagiarism:")
        print(f"- Type: {type(plagiarism)}")
        print(f"- Contenu: {plagiarism}")
        print(f"- Percent: {plagiarism.get('percent')} (type: {type(plagiarism.get('percent'))})")
        print()
        
        # Vérifier la structure ai_content
        ai_content = result.get('ai_content', {})
        print(f"AI Content:")
        print(f"- Type: {type(ai_content)}")
        print(f"- Contenu: {ai_content}")
        print(f"- Percent: {ai_content.get('percent')} (type: {type(ai_content.get('percent'))})")
        print()
        
        # Simuler l'extraction des valeurs comme dans routes.py
        print("Simulation extraction routes.py:")
        plagiarism_score = result['plagiarism']['percent']
        print(f"plagiarism_score = {plagiarism_score} (type: {type(plagiarism_score)})")
        
        ai_content = result.get('ai_content', {})
        if isinstance(ai_content, dict):
            ai_score = ai_content.get('percent', 0)
        else:
            ai_score = 0
        print(f"ai_score = {ai_score} (type: {type(ai_score)})")
        
        sources_count = result['plagiarism']['sources_found']
        print(f"sources_count = {sources_count} (type: {type(sources_count)})")
        
        provider_used = result.get('provider_used', 'unknown')
        print(f"provider_used = {provider_used}")
        
        print()
        print("✅ Extraction réussie - Pas de problème dans la structure des données")
    else:
        print("❌ Aucun résultat retourné")

if __name__ == "__main__":
    debug_result_processing()