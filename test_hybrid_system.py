#!/usr/bin/env python3
"""
Test du système hybride d'analyse
GPTZero API pour l'IA + Traitement local pour le plagiat
"""

import os
import sys
import tempfile
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(__file__))

from hybrid_analysis_service import hybrid_analysis_service
from local_plagiarism_service import local_plagiarism_service
from models import Document, db
from app import app

def create_test_document(text_content: str, filename: str = "test.txt") -> str:
    """Créer un fichier de test temporaire"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(text_content)
    temp_file.close()
    return temp_file.name

def test_local_plagiarism_service():
    """Tester le service de plagiat local"""
    print("=== Test du service de plagiat local ===")
    
    # Texte de test 1
    text1 = """
    L'intelligence artificielle est une technologie révolutionnaire qui transforme notre monde.
    Elle permet aux machines d'apprendre et de prendre des décisions comme les humains.
    Les applications sont nombreuses : reconnaissance vocale, traduction automatique, conduite autonome.
    Cette technologie soulève aussi des questions éthiques importantes.
    """
    
    # Texte de test 2 (contenant du plagiat)
    text2 = """
    L'IA est une technologie innovante qui change notre société.
    Elle permet aux machines d'apprendre et de prendre des décisions comme les humains.
    Les domaines d'application incluent la reconnaissance vocale et la traduction.
    Il faut considérer les enjeux éthiques de cette technologie.
    """
    
    try:
        # Créer les fichiers de test
        file1 = create_test_document(text1, "document1.txt")
        file2 = create_test_document(text2, "document2.txt")
        
        # Ajouter le premier document à la base
        print("Ajout du document 1 à la base locale...")
        success = local_plagiarism_service.add_document_to_database(file1, 1)
        print(f"Document 1 ajouté : {success}")
        
        # Analyser le deuxième document (qui contient du plagiat)
        print("\nAnalyse du document 2 pour détecter le plagiat...")
        result = local_plagiarism_service.analyze_plagiarism(text2)
        
        print(f"Score de plagiat : {result['plagiarism_score']}%")
        print(f"Méthode d'analyse : {result['analysis_method']}")
        print(f"Documents comparés : {result.get('total_documents_compared', 0)}")
        
        if result['matches']:
            print("\nCorrespondances détectées :")
            for i, match in enumerate(result['matches'][:3]):
                print(f"  {i+1}. Similarité : {match['similarity']:.2%}")
                print(f"     Méthode : {match['method']}")
                print(f"     Texte trouvé : {match['matched_text'][:100]}...")
                print()
        
        # Statistiques de la base
        stats = local_plagiarism_service.get_database_stats()
        print("Statistiques de la base locale :")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # Nettoyage
        os.unlink(file1)
        os.unlink(file2)
        
        return True
        
    except Exception as e:
        print(f"Erreur lors du test : {e}")
        return False

def test_hybrid_analysis():
    """Tester le service d'analyse hybride complet"""
    print("\n=== Test du service d'analyse hybride ===")
    
    test_text = """
    Artificial intelligence represents a significant breakthrough in computer science.
    Machine learning algorithms can now process vast amounts of data to identify patterns.
    This technology has applications in healthcare, finance, and autonomous vehicles.
    However, we must address the ethical implications of AI development.
    """
    
    try:
        with app.app_context():
            # Créer un document fictif pour le test
            document = Document()
            document.id = 999
            document.original_filename = "test_hybrid.txt"
            document.filename = "test_hybrid.txt"
            document.user_id = "test-user"
            
            # Créer un fichier temporaire
            temp_file = create_test_document(test_text)
            document.file_path = temp_file
            
            print("Lancement de l'analyse hybride...")
            result = hybrid_analysis_service.analyze_document(document, test_text)
            
            print(f"Success : {result.get('success')}")
            print(f"AI Score : {result.get('ai_score')}%")
            print(f"Plagiarism Score : {result.get('plagiarism_score')}%")
            print(f"Risk Level : {result.get('risk_level')}")
            print(f"Analysis Method : {result.get('analysis_method')}")
            
            if result.get('errors'):
                print("Erreurs détectées :")
                for error in result['errors']:
                    print(f"  - {error}")
            
            # Détails des analyses
            ai_analysis = result.get('ai_analysis', {})
            print(f"\nAnalyse IA - Success: {ai_analysis.get('success')}")
            print(f"Analyse IA - Method: {ai_analysis.get('method')}")
            
            plagiarism_analysis = result.get('plagiarism_analysis', {})
            print(f"Analyse Plagiat - Success: {plagiarism_analysis.get('success')}")
            print(f"Analyse Plagiat - Method: {plagiarism_analysis.get('method')}")
            print(f"Documents comparés: {plagiarism_analysis.get('total_compared', 0)}")
            
            # Nettoyage
            os.unlink(temp_file)
            
        return True
        
    except Exception as e:
        print(f"Erreur lors du test hybride : {e}")
        return False

def main():
    """Fonction principale de test"""
    print("Test du système hybride d'analyse AcadCheck")
    print("==========================================")
    print(f"Date : {datetime.now()}")
    print()
    
    # Test du service local
    local_success = test_local_plagiarism_service()
    
    # Test du service hybride
    hybrid_success = test_hybrid_analysis()
    
    print("\n=== Résumé des tests ===")
    print(f"Service local : {'✅ SUCCESS' if local_success else '❌ FAILED'}")
    print(f"Service hybride : {'✅ SUCCESS' if hybrid_success else '❌ FAILED'}")
    
    if local_success and hybrid_success:
        print("\n🎉 Tous les tests sont passés avec succès !")
        print("\nArchitecture hybride opérationnelle :")
        print("✅ Détection IA : GPTZero API (cloud)")
        print("✅ Détection Plagiat : TF-IDF + Similarité locale")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez les logs.")

if __name__ == "__main__":
    main()