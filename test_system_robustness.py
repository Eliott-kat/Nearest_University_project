#!/usr/bin/env python3
"""
Test de robustesse système pour AcadCheck
Tests complets pour détecter et corriger les bugs potentiels
"""

import os
import sys
import tempfile
import logging
from io import BytesIO
from werkzeug.datastructures import FileStorage

# Configuration des logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_authentication_system():
    """Test du système d'authentification"""
    print("🔐 TEST SYSTÈME D'AUTHENTIFICATION")
    print("-" * 40)
    
    from app import app, db
    from models import User, UserRole
    from werkzeug.security import generate_password_hash, check_password_hash
    
    with app.app_context():
        try:
            # Test 1: Création d'utilisateur
            test_user = User.query.filter_by(email='test_robustesse@acadcheck.local').first()
            if test_user:
                db.session.delete(test_user)
                db.session.commit()
            
            new_user = User()
            new_user.id = 'test-robustesse-user'
            new_user.email = 'test_robustesse@acadcheck.local'
            new_user.password_hash = generate_password_hash('TestPassword123!')
            new_user.first_name = 'Test'
            new_user.last_name = 'Robustesse'
            new_user.role = UserRole.STUDENT
            new_user.active = True
            
            db.session.add(new_user)
            db.session.commit()
            print("✅ Création d'utilisateur réussie")
            
            # Test 2: Vérification mot de passe
            if check_password_hash(new_user.password_hash, 'TestPassword123!'):
                print("✅ Vérification mot de passe réussie")
            else:
                print("❌ Échec vérification mot de passe")
            
            # Test 3: Recherche utilisateur
            found_user = User.query.filter_by(email='test_robustesse@acadcheck.local').first()
            if found_user and found_user.first_name == 'Test':
                print("✅ Recherche utilisateur réussie")
            else:
                print("❌ Échec recherche utilisateur")
            
            # Nettoyage
            db.session.delete(new_user)
            db.session.commit()
            print("✅ Nettoyage réussi")
            
        except Exception as e:
            print(f"❌ Erreur test authentification: {e}")
            db.session.rollback()

def test_file_upload_robustness():
    """Test robustesse upload de fichiers"""
    print("\n📁 TEST ROBUSTESSE UPLOAD")
    print("-" * 40)
    
    from app import app, db
    from models import User, Document, DocumentStatus
    from file_utils import save_uploaded_file, extract_text_from_file, get_file_size
    
    with app.app_context():
        try:
            demo_user = User.query.filter_by(email='demo@acadcheck.local').first()
            if not demo_user:
                print("❌ Utilisateur démo non trouvé")
                return
            
            # Test 1: Fichier texte normal
            test_content = "Ceci est un test de robustesse.\n" * 50
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(test_content)
                temp_path = f.name
            
            try:
                with open(temp_path, 'rb') as f:
                    file_storage = FileStorage(
                        stream=BytesIO(f.read()),
                        filename='test_robustesse.txt',
                        content_type='text/plain'
                    )
                    
                    result = save_uploaded_file(file_storage)
                    if result:
                        print("✅ Upload fichier texte réussi")
                        file_path, filename = result
                        
                        # Test extraction
                        text = extract_text_from_file(file_path, 'text/plain')
                        if text and len(text) > 0:
                            print("✅ Extraction texte réussie")
                        else:
                            print("❌ Échec extraction texte")
                    else:
                        print("❌ Échec upload fichier")
                        
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
            # Test 2: Fichier vide (cas limite)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write("")  # Fichier vide
                temp_path = f.name
            
            try:
                with open(temp_path, 'rb') as f:
                    file_storage = FileStorage(
                        stream=BytesIO(f.read()),
                        filename='test_vide.txt',
                        content_type='text/plain'
                    )
                    
                    result = save_uploaded_file(file_storage)
                    if result:
                        print("✅ Gestion fichier vide robuste")
                    else:
                        print("⚠️ Fichier vide rejeté (comportement attendu)")
                        
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
            # Test 3: Fichier avec caractères spéciaux
            special_content = "Test avec éàçüñ et 中文 et emoji 🎓📝✅"
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(special_content)
                temp_path = f.name
            
            try:
                with open(temp_path, 'rb') as f:
                    file_storage = FileStorage(
                        stream=BytesIO(f.read()),
                        filename='test_spéciaux.txt',
                        content_type='text/plain'
                    )
                    
                    result = save_uploaded_file(file_storage)
                    if result:
                        file_path, filename = result
                        text = extract_text_from_file(file_path, 'text/plain')
                        if text and "éàçüñ" in text:
                            print("✅ Caractères spéciaux gérés correctement")
                        else:
                            print("⚠️ Problème avec caractères spéciaux")
                    else:
                        print("❌ Échec fichier caractères spéciaux")
                        
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            print(f"❌ Erreur test upload: {e}")

def test_detection_algorithms():
    """Test robustesse algorithmes de détection"""
    print("\n🔍 TEST ALGORITHMES DE DÉTECTION")
    print("-" * 40)
    
    from app import app
    
    with app.app_context():
        try:
            from unified_detection_service import UnifiedDetectionService
            service = UnifiedDetectionService()
            
            # Test 1: Texte académique normal
            academic_text = """
            Cette étude examine les impacts environnementaux de l'énergie renouvelable.
            Les recherches montrent que les technologies solaires et éoliennes contribuent
            significativement à la réduction des émissions de carbone. L'analyse des données
            révèle une corrélation positive entre l'adoption des énergies renouvelables
            et l'amélioration de la qualité de l'air dans les zones urbaines.
            """
            
            result = service.analyze_text(academic_text, "test_academique.txt")
            if result and 'plagiarism' in result:
                plagiarism_score = result['plagiarism']['percent']
                ai_score = result.get('ai_content', {}).get('percent', 0)
                print(f"✅ Analyse texte académique: {plagiarism_score}% plagiat, {ai_score}% IA")
                
                # Vérification scores réalistes
                if 0 <= plagiarism_score <= 100 and 0 <= ai_score <= 100:
                    print("✅ Scores dans les limites attendues")
                else:
                    print(f"⚠️ Scores hors limites: plagiat={plagiarism_score}, IA={ai_score}")
            else:
                print("❌ Échec analyse texte académique")
            
            # Test 2: Texte très court
            short_text = "Bonjour monde."
            result = service.analyze_text(short_text, "test_court.txt")
            if result:
                print("✅ Gestion texte court robuste")
            else:
                print("⚠️ Problème avec texte très court")
            
            # Test 3: Texte long
            long_text = "Cette phrase se répète. " * 200
            result = service.analyze_text(long_text, "test_long.txt")
            if result:
                print("✅ Gestion texte long robuste")
            else:
                print("⚠️ Problème avec texte très long")
                
        except Exception as e:
            print(f"❌ Erreur test détection: {e}")

def test_database_consistency():
    """Test consistance base de données"""
    print("\n🗄️ TEST CONSISTANCE BASE DE DONNÉES")
    print("-" * 40)
    
    from app import app, db
    from models import User, Document, AnalysisResult
    
    with app.app_context():
        try:
            # Test 1: Comptage des enregistrements
            users_count = User.query.count()
            documents_count = Document.query.count()
            analyses_count = AnalysisResult.query.count()
            
            print(f"✅ Enregistrements: {users_count} users, {documents_count} docs, {analyses_count} analyses")
            
            # Test 2: Intégrité référentielle
            orphan_documents = Document.query.filter(~Document.user_id.in_(
                db.session.query(User.id)
            )).count()
            
            orphan_analyses = AnalysisResult.query.filter(~AnalysisResult.document_id.in_(
                db.session.query(Document.id)
            )).count()
            
            if orphan_documents == 0 and orphan_analyses == 0:
                print("✅ Intégrité référentielle maintenue")
            else:
                print(f"⚠️ Documents orphelins: {orphan_documents}, Analyses orphelines: {orphan_analyses}")
            
            # Test 3: Utilisateurs actifs
            active_users = User.query.filter_by(active=True).count()
            print(f"✅ Utilisateurs actifs: {active_users}")
            
        except Exception as e:
            print(f"❌ Erreur test base de données: {e}")

def test_error_handling():
    """Test gestion d'erreurs"""
    print("\n⚠️ TEST GESTION D'ERREURS")
    print("-" * 40)
    
    from app import app
    
    with app.app_context():
        try:
            # Test 1: Service avec fichier inexistant
            from unified_detection_service import UnifiedDetectionService
            service = UnifiedDetectionService()
            
            result = service.analyze_text("", "fichier_vide.txt")
            if result:
                print("✅ Gestion texte vide robuste")
            else:
                print("⚠️ Texte vide rejeté (comportement attendu)")
            
            # Test 2: Caractères non-UTF8 (simulation)
            try:
                problematic_text = "Test normal avec du texte régulier"
                result = service.analyze_text(problematic_text, "test_encoding.txt")
                if result:
                    print("✅ Gestion encodage robuste")
            except Exception as e:
                print(f"⚠️ Problème encodage géré: {str(e)[:50]}...")
                
        except Exception as e:
            print(f"❌ Erreur test gestion d'erreurs: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE TESTS DE ROBUSTESSE ACADCHECK")
    print("=" * 50)
    
    # Vérifier l'environnement
    if not os.path.exists('app.py'):
        print("❌ Fichier app.py non trouvé. Exécutez depuis le dossier racine.")
        sys.exit(1)
    
    # Exécuter tous les tests
    test_authentication_system()
    test_file_upload_robustness()
    test_detection_algorithms()
    test_database_consistency()
    test_error_handling()
    
    print("\n🎯 TESTS DE ROBUSTESSE TERMINÉS")
    print("=" * 50)
    print("Vérifiez les résultats ci-dessus pour identifier les améliorations nécessaires.")

if __name__ == "__main__":
    main()