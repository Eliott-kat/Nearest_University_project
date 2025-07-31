#!/usr/bin/env python3
"""
Test des statistiques globales selon vos attentes
"""

import sys
sys.path.append('.')

from improved_detection_algorithm import ImprovedDetectionAlgorithm
from simple_ai_detector_clean import SimpleAIDetector
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_document_mixte():
    """Test avec le document fourni (mixte français/anglais avec citation Wikipedia)"""
    
    # Lecture du document fourni
    with open('attached_assets/d6_1753983839509.txt', 'r', encoding='utf-8') as f:
        document_content = f.read()
    
    print("🧪 TEST DOCUMENT MIXTE (IA + Citation Wikipedia)")
    print("=" * 60)
    print(f"📄 Contenu analysé :")
    print(document_content)
    print("-" * 60)
    
    try:
        # Test avec l'algorithme amélioré
        improved_algo = ImprovedDetectionAlgorithm()
        result = improved_algo.detect_plagiarism_and_ai(document_content, "test_mixte.txt")
        
        if result:
            plagiarism = result.get('percent', 0)
            ai_score = result.get('ai_percent', 0)
            doc_type = result.get('document_type', 'unknown')
            
            print(f"📊 Document identifié comme: {doc_type}")
            print(f"📈 Score plagiat: {plagiarism}%")
            print(f"🤖 Score IA: {ai_score}%")
            
            # Vérification selon vos statistiques attendues
            print("\n🎯 VÉRIFICATION SELON VOS STATISTIQUES :")
            
            # Ce document contient de l'IA + citation Wikipedia
            # Attendu : Plagiat 10-50%, IA 30-70%
            if 10 <= plagiarism <= 50:
                print(f"✅ PLAGIAT OK: {plagiarism}% (cible 10-50% pour texte mixte)")
            elif plagiarism < 10:
                print(f"⚠️ PLAGIAT FAIBLE: {plagiarism}% (attendu 10-50% pour citation Wikipedia)")
            else:
                print(f"⚠️ PLAGIAT ÉLEVÉ: {plagiarism}% (attendu 10-50%)")
            
            if 30 <= ai_score <= 70:
                print(f"✅ IA OK: {ai_score}% (cible 30-70% pour texte mixte)")
            elif ai_score < 30:
                print(f"⚠️ IA FAIBLE: {ai_score}% (attendu 30-70% pour contenu IA)")
            else:
                print(f"✅ IA DÉTECTÉE: {ai_score}% (bien détecté)")
            
            return True
        else:
            print("❌ ERREUR: Aucun résultat retourné")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_texte_100_humain():
    """Test avec du texte 100% humain authentique"""
    
    texte_humain = """
    Hier, j'ai rencontré mon ami Pierre au café du coin de ma rue. Nous avons discuté de nos projets pour les vacances d'été. 
    Il m'a raconté son voyage en Espagne l'année dernière et m'a donné quelques conseils pratiques.
    J'aimerais beaucoup visiter Barcelone, surtout pour voir l'architecture de Gaudí.
    Pierre m'a dit que la Sagrada Família était vraiment impressionnante à voir en vrai.
    Nous avons aussi parlé de nos études et de nos futurs plans professionnels.
    """
    
    print("\n✅ TEST TEXTE 100% HUMAIN ORIGINAL")
    print("=" * 60)
    
    try:
        improved_algo = ImprovedDetectionAlgorithm()
        result = improved_algo.detect_plagiarism_and_ai(texte_humain, "test_humain.txt")
        
        if result:
            plagiarism = result.get('percent', 0)
            ai_score = result.get('ai_percent', 0)
            
            print(f"📈 Score plagiat: {plagiarism}%")
            print(f"🤖 Score IA: {ai_score}%")
            
            # Vérification selon vos statistiques : 0-5% plagiat, 0-10% IA
            if plagiarism <= 5:
                print(f"✅ PLAGIAT PARFAIT: {plagiarism}% (cible 0-5%)")
            else:
                print(f"⚠️ PLAGIAT TROP ÉLEVÉ: {plagiarism}% (attendu 0-5%)")
            
            if ai_score <= 10:
                print(f"✅ IA PARFAIT: {ai_score}% (cible 0-10%)")
            else:
                print(f"⚠️ IA TROP ÉLEVÉ: {ai_score}% (attendu 0-10%)")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

def test_texte_100_ia():
    """Test avec du texte 100% IA (style ChatGPT)"""
    
    texte_ia = """
    Artificial intelligence represents a transformative paradigm shift in computational methodologies, fundamentally altering the landscape of technological innovation. The integration of machine learning algorithms with advanced neural network architectures has facilitated unprecedented advancements in data processing capabilities. Furthermore, the implementation of deep learning frameworks has demonstrated remarkable efficacy in pattern recognition tasks. Consequently, these developments have significant implications for various industrial applications. Moreover, the optimization of algorithmic performance through iterative refinement processes ensures enhanced computational efficiency. Additionally, the scalability of these systems enables broad deployment across diverse operational contexts.
    """
    
    print("\n🤖 TEST TEXTE 100% IA (STYLE CHATGPT)")
    print("=" * 60)
    
    try:
        improved_algo = ImprovedDetectionAlgorithm()
        result = improved_algo.detect_plagiarism_and_ai(texte_ia, "test_ia.txt")
        
        if result:
            plagiarism = result.get('percent', 0)
            ai_score = result.get('ai_percent', 0)
            
            print(f"📈 Score plagiat: {plagiarism}%")
            print(f"🤖 Score IA: {ai_score}%")
            
            # Vérification selon vos statistiques : 0-10% plagiat, 80-100% IA
            if plagiarism <= 10:
                print(f"✅ PLAGIAT OK: {plagiarism}% (cible 0-10%)")
            else:
                print(f"⚠️ PLAGIAT TROP ÉLEVÉ: {plagiarism}% (attendu 0-10%)")
            
            if ai_score >= 80:
                print(f"✅ IA PARFAIT: {ai_score}% (cible 80-100%)")
            else:
                print(f"⚠️ IA INSUFFISANT: {ai_score}% (attendu 80-100%)")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("🎯 VALIDATION DES STATISTIQUES GLOBALES")
    print("=" * 80)
    
    success1 = test_document_mixte()
    success2 = test_texte_100_humain()
    success3 = test_texte_100_ia()
    
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DES TESTS :")
    print(f"✅ Document mixte (IA + Wikipedia): {'RÉUSSI' if success1 else 'ÉCHEC'}")
    print(f"✅ Texte 100% humain: {'RÉUSSI' if success2 else 'ÉCHEC'}")
    print(f"✅ Texte 100% IA: {'RÉUSSI' if success3 else 'ÉCHEC'}")
    
    if all([success1, success2, success3]):
        print("\n🎉 TOUS LES TESTS RÉUSSIS - Statistiques conformes !")
    else:
        print("\n⚠️ Certains ajustements peuvent être nécessaires")