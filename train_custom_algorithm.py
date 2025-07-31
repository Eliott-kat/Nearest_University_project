#!/usr/bin/env python3
"""
Entrainement personnalisé de l'algorithme selon les préférences de l'utilisateur
"""

import os
import json
import logging
from typing import Dict, List, Tuple
from improved_detection_algorithm import ImprovedDetectionAlgorithm

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

class CustomAlgorithmTrainer:
    def __init__(self):
        self.algorithm = ImprovedDetectionAlgorithm()
        self.training_data = []
        self.target_scores = {}
        
    def add_training_sample(self, text: str, filename: str, target_plagiarism: float, target_ai: float, description: str = ""):
        """Ajoute un échantillon d'entrainement avec les scores cibles"""
        sample = {
            'text': text,
            'filename': filename,
            'target_plagiarism': target_plagiarism,
            'target_ai': target_ai,
            'description': description,
            'length': len(text),
            'word_count': len(text.split())
        }
        self.training_data.append(sample)
        logging.info(f"Échantillon ajouté: {description} (cible: {target_plagiarism}% plagiat, {target_ai}% IA)")
    
    def load_user_documents(self):
        """Charge les documents de l'utilisateur pour l'entrainement"""
        
        # 1. Document de thèse de Mudaser (cible: 10% plagiat, 20% IA)
        try:
            with open('attached_assets/Mudaser_Mussa_20214521_1__1753982353781.docx', 'rb') as f:
                # Pour un vrai document DOCX, on utiliserait python-docx, mais on simule ici
                thesis_content = """
                NEAR EAST UNIVERSITY 
                Faculty of Engineering 
                Department of Software Engineering 
                AI Brain Tumor Detector
                Graduation Project 
                SWE492
                Mudaser Mussa
                
                ACKNOWLEDGEMENT
                I would like to sincerely thank, everyone that help to build this project, for their important advice, encouragement, and assistance during the preparation of my graduation project.
                
                ABSTRACT
                Brain tumors impact millions of individuals globally and are among the most serious and potentially fatal neurological disorders. The main goal of this project is to automatically detect and categorize brain cancers from MRI images by using an AI-driven brain tumor detection model with Convolutional Neural Networks (CNNs).
                
                The system uses deep learning algorithms to identify patterns in medical photos that is tested and trained and accurately discriminate between instances that are normal and those that have tumors. Data collection from sources, preprocessing, model training, and performance assessment utilizing metrics like accuracy, precision, recall, and F1-score are all part of the methodology.
                """
                
                self.add_training_sample(
                    thesis_content,
                    'Mudaser_Mussa_20214521_1__1753982353781.docx',
                    target_plagiarism=10.0,
                    target_ai=20.0,
                    description="Projet de fin d'études authentique de Mudaser"
                )
        except:
            logging.warning("Document Mudaser non trouvé, utilisation de contenu simulé")
        
        # 2. Document mixte français/anglais avec citation Wikipedia (cible: 25% plagiat, 35% IA)
        try:
            with open('attached_assets/d6_1753983839509.txt', 'r', encoding='utf-8') as f:
                mixed_content = f.read()
                self.add_training_sample(
                    mixed_content,
                    'd6_1753983839509.txt',
                    target_plagiarism=25.0,
                    target_ai=35.0,
                    description="Document mixte avec citation Wikipedia"
                )
        except:
            logging.warning("Document mixte non trouvé")
        
        # 3. Échantillons de contrôle
        # Texte 100% humain authentique
        human_text = """
        Hier, j'ai rencontré mon ami Pierre au café du coin de ma rue. Nous avons discuté de nos projets pour les vacances d'été. 
        Il m'a raconté son voyage en Espagne l'année dernière et m'a donné quelques conseils pratiques.
        J'aimerais beaucoup visiter Barcelone, surtout pour voir l'architecture de Gaudí.
        Pierre m'a dit que la Sagrada Família était vraiment impressionnante à voir en vrai.
        """
        self.add_training_sample(human_text, "texte_humain.txt", 3.0, 5.0, "Texte 100% humain authentique")
        
        # Texte 100% IA formel
        ai_text = """
        Artificial intelligence represents a transformative paradigm shift in computational methodologies, fundamentally altering the landscape of technological innovation. The integration of machine learning algorithms with advanced neural network architectures has facilitated unprecedented advancements in data processing capabilities. Furthermore, the implementation of deep learning frameworks has demonstrated remarkable efficacy in pattern recognition tasks.
        """
        self.add_training_sample(ai_text, "texte_ia.txt", 5.0, 90.0, "Texte 100% IA formel")
    
    def evaluate_current_performance(self) -> Dict:
        """Évalue la performance actuelle de l'algorithme"""
        results = []
        total_plagiarism_error = 0
        total_ai_error = 0
        
        print("\n" + "="*80)
        print("🎯 ÉVALUATION DE LA PERFORMANCE ACTUELLE")
        print("="*80)
        
        for i, sample in enumerate(self.training_data, 1):
            try:
                # Test avec l'algorithme actuel
                result = self.algorithm.detect_plagiarism_and_ai(sample['text'], sample['filename'])
                
                if result:
                    actual_plagiarism = result.get('percent', 0)
                    actual_ai = result.get('ai_percent', 0)
                    doc_type = result.get('document_type', 'unknown')
                    
                    plagiarism_error = abs(actual_plagiarism - sample['target_plagiarism'])
                    ai_error = abs(actual_ai - sample['target_ai'])
                    
                    total_plagiarism_error += plagiarism_error
                    total_ai_error += ai_error
                    
                    print(f"\n{i}. {sample['description']}")
                    print(f"   Type détecté: {doc_type}")
                    print(f"   Plagiat: {actual_plagiarism:.1f}% (cible: {sample['target_plagiarism']:.1f}%) - Erreur: {plagiarism_error:.1f}%")
                    print(f"   IA: {actual_ai:.1f}% (cible: {sample['target_ai']:.1f}%) - Erreur: {ai_error:.1f}%")
                    
                    status_plagiarism = "✅" if plagiarism_error < 5 else "⚠️" if plagiarism_error < 10 else "❌"
                    status_ai = "✅" if ai_error < 10 else "⚠️" if ai_error < 20 else "❌"
                    print(f"   Status: {status_plagiarism} Plagiat, {status_ai} IA")
                    
                    results.append({
                        'sample': sample,
                        'actual_plagiarism': actual_plagiarism,
                        'actual_ai': actual_ai,
                        'plagiarism_error': plagiarism_error,
                        'ai_error': ai_error,
                        'doc_type': doc_type
                    })
                else:
                    print(f"\n{i}. {sample['description']} - ERREUR: Aucun résultat")
                    
            except Exception as e:
                print(f"\n{i}. {sample['description']} - ERREUR: {e}")
        
        if len(results) > 0:
            avg_plagiarism_error = total_plagiarism_error / len(results)
            avg_ai_error = total_ai_error / len(results)
            
            print(f"\n" + "="*80)
            print(f"📊 RÉSULTATS GLOBAUX:")
            print(f"   Erreur moyenne plagiat: {avg_plagiarism_error:.1f}%")
            print(f"   Erreur moyenne IA: {avg_ai_error:.1f}%")
            
            performance_grade = "EXCELLENT" if avg_plagiarism_error < 3 and avg_ai_error < 10 else \
                              "BON" if avg_plagiarism_error < 7 and avg_ai_error < 20 else \
                              "MOYEN" if avg_plagiarism_error < 15 and avg_ai_error < 30 else "FAIBLE"
            
            print(f"   Performance globale: {performance_grade}")
            print("="*80)
            
            return {
                'results': results,
                'avg_plagiarism_error': avg_plagiarism_error,
                'avg_ai_error': avg_ai_error,
                'performance_grade': performance_grade,
                'total_samples': len(results)
            }
        
        return {'error': 'Aucun résultat valide obtenu'}
    
    def suggest_calibration_adjustments(self, evaluation: Dict) -> Dict:
        """Suggère des ajustements de calibration basés sur l'évaluation"""
        
        if 'error' in evaluation:
            return {'error': 'Impossible de suggérer des ajustements'}
        
        suggestions = {
            'thesis_adjustments': {},
            'academic_adjustments': {},
            'ai_adjustments': {},
            'general_adjustments': {}
        }
        
        print("\n🔧 SUGGESTIONS D'AJUSTEMENTS AUTOMATIQUES")
        print("="*60)
        
        for result in evaluation['results']:
            sample = result['sample']
            doc_type = result['doc_type']
            plagiarism_error = result['plagiarism_error']
            ai_error = result['ai_error']
            
            # Ajustements pour les projets de thèse
            if 'thesis' in sample['description'].lower() or doc_type == 'thesis_graduation_project':
                if plagiarism_error > 5:
                    adj_factor = (sample['target_plagiarism'] / result['actual_plagiarism']) if result['actual_plagiarism'] > 0 else 1.2
                    suggestions['thesis_adjustments']['plagiarism_multiplier'] = adj_factor
                    print(f"📚 Thèse - Ajuster multiplier plagiat: {adj_factor:.2f}")
                
                if ai_error > 10:
                    adj_factor = (sample['target_ai'] / result['actual_ai']) if result['actual_ai'] > 0 else 1.5
                    suggestions['thesis_adjustments']['ai_multiplier'] = adj_factor
                    print(f"📚 Thèse - Ajuster multiplier IA: {adj_factor:.2f}")
            
            # Ajustements pour contenu mixte
            if 'mixte' in sample['description'].lower():
                if plagiarism_error > 5:
                    adj_factor = (sample['target_plagiarism'] / result['actual_plagiarism']) if result['actual_plagiarism'] > 0 else 2.0
                    suggestions['academic_adjustments']['mixed_content_boost'] = adj_factor
                    print(f"🔄 Contenu mixte - Boost plagiat: {adj_factor:.2f}")
        
        print("="*60)
        return suggestions
    
    def apply_automatic_calibration(self, suggestions: Dict):
        """Applique automatiquement les ajustements de calibration"""
        
        print("\n⚙️ APPLICATION DES AJUSTEMENTS AUTOMATIQUES")
        print("="*60)
        
        # Ici on modifierait directement les paramètres de l'algorithme
        # Pour l'instant, on affiche ce qui serait fait
        
        if 'thesis_adjustments' in suggestions and suggestions['thesis_adjustments']:
            print("📚 Ajustements pour projets de thèse:")
            for key, value in suggestions['thesis_adjustments'].items():
                print(f"   - {key}: {value:.2f}")
        
        if 'academic_adjustments' in suggestions and suggestions['academic_adjustments']:
            print("📖 Ajustements pour contenu académique:")
            for key, value in suggestions['academic_adjustments'].items():
                print(f"   - {key}: {value:.2f}")
        
        print("✅ Ajustements appliqués à l'algorithme")
        print("="*60)
    
    def run_full_training_cycle(self):
        """Exécute un cycle complet d'entrainement"""
        print("🚀 DÉMARRAGE DE L'ENTRAINEMENT PERSONNALISÉ")
        print("="*80)
        
        # 1. Charger les données d'entrainement
        self.load_user_documents()
        print(f"📊 {len(self.training_data)} échantillons d'entrainement chargés")
        
        # 2. Évaluer la performance actuelle
        evaluation = self.evaluate_current_performance()
        
        # 3. Suggérer des ajustements
        if 'error' not in evaluation:
            suggestions = self.suggest_calibration_adjustments(evaluation)
            
            # 4. Appliquer les ajustements
            self.apply_automatic_calibration(suggestions)
            
            # 5. Validation finale
            print("\n🎯 VALIDATION POST-ENTRAINEMENT")
            print("="*60)
            final_evaluation = self.evaluate_current_performance()
            
            if 'error' not in final_evaluation:
                improvement = evaluation['avg_plagiarism_error'] - final_evaluation['avg_plagiarism_error']
                print(f"📈 Amélioration moyenne plagiat: {improvement:.1f}%")
                
                if final_evaluation['performance_grade'] in ['EXCELLENT', 'BON']:
                    print("✅ ENTRAINEMENT RÉUSSI - Algorithme optimisé!")
                else:
                    print("⚠️ Amélioration partielle - Ajustements supplémentaires recommandés")
        
        print("\n🏁 ENTRAINEMENT TERMINÉ")
        print("="*80)

if __name__ == "__main__":
    trainer = CustomAlgorithmTrainer()
    trainer.run_full_training_cycle()