#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de débogage de l'algorithme de détection
"""

import os
import sys
sys.path.append('.')

from unified_detection_service import UnifiedDetectionService
from sentence_bert_detection import SentenceBertDetection
from utils.ai_gptzero_like import AIDetectionService

def test_algorithm():
    """Test simple de l'algorithme avec du texte connu"""
    
    # Texte de test avec du contenu clairement problématique
    test_text = """
    La biodiversité est l'ensemble des êtres vivants ainsi que les écosystèmes dans lesquels ils évoluent. 
    Ce terme comprend également les interactions des espèces entre elles et avec leurs milieux. 
    La biodiversité fait partie intégrante du fonctionnement de la biosphère et de sa capacité d'adaptation. 
    Elle est considérée comme une des ressources vitales du développement durable.
    
    Les écosystèmes forestiers abritent plus de 80% de la biodiversité terrestre mondiale.
    Ces environnements complexes constituent des réservoirs génétiques essentiels pour l'humanité.
    La déforestation représente une menace majeure pour la conservation de cette richesse biologique.
    Les forêts tropicales, en particulier, contiennent une diversité exceptionnelle d'espèces endémiques.
    """
    
    print("🔬 Test de l'algorithme de détection")
    print("=" * 50)
    
    try:
        # Test 1: Service unifié
        print("\n1. Test du service unifié:")
        unified_service = UnifiedDetectionService()
        result = unified_service.analyze_text(test_text, "test_debug.txt")
        
        if result and 'success' in result:
            print(f"✅ Résultat unifié: {result['plagiarism_score']}% plagiat, {result['ai_score']}% IA")
            print(f"   Service utilisé: {result.get('service_used', 'inconnu')}")
        else:
            print(f"❌ Échec du service unifié: {result}")
            
    except Exception as e:
        print(f"❌ Erreur service unifié: {str(e)}")
        import traceback
        traceback.print_exc()
    
    try:
        # Test 2: Sentence-BERT seul
        print("\n2. Test Sentence-BERT:")
        bert_detector = SentenceBertDetection()
        bert_result = bert_detector.detect_plagiarism(test_text)
        
        if bert_result:
            print(f"✅ Sentence-BERT: {bert_result.get('similarity_score', 0):.1f}% de similarité")
            print(f"   Phrases détectées: {len(bert_result.get('highlighted_sentences', []))}")
        else:
            print("❌ Échec Sentence-BERT")
            
    except Exception as e:
        print(f"❌ Erreur Sentence-BERT: {str(e)}")
        import traceback
        traceback.print_exc()
    
    try:
        # Test 3: Détection IA seule
        print("\n3. Test détection IA:")
        ai_detector = AIDetectionService()
        ai_result = ai_detector.detect_ai_content(test_text)
        
        if ai_result:
            print(f"✅ Détection IA: {ai_result.get('ai_probability', 0):.1f}% IA détectée")
            print(f"   Phrases analysées: {len(ai_result.get('sentence_scores', []))}")
        else:
            print("❌ Échec détection IA")
            
    except Exception as e:
        print(f"❌ Erreur détection IA: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Vérifier la base de données locale
    print("\n4. Vérification base de données:")
    try:
        import sqlite3
        db_path = "sentence_bert_database.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            count = cursor.fetchone()[0]
            print(f"✅ Base de données: {count} documents stockés")
            conn.close()
        else:
            print("⚠️ Base de données non trouvée")
    except Exception as e:
        print(f"❌ Erreur base de données: {str(e)}")

if __name__ == "__main__":
    test_algorithm()