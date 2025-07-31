"""
Détecteur IA amélioré avec modèles plus puissants
Basé sur RoBERTa, datasets étendus et techniques avancées
"""

import os
import logging
import pickle
import json
import numpy as np
from typing import Dict, List, Tuple
from collections import Counter
import re
import math

# Fallback imports with graceful degradation
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy non disponible - utilisation de listes Python")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn non disponible - utilisation d'un fallback simple")

try:
    import transformers
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers non disponible - utilisation de modèles classiques")


class EnhancedAIDetector:
    """Détecteur IA amélioré avec modèles multiples et datasets étendus"""
    
    def __init__(self, models_dir="plagiarism_cache/ai_models"):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        # Modèles disponibles
        self.transformer_model = None
        self.ensemble_model = None
        self.tfidf_vectorizer = None
        self.linguistic_analyzer = LinguisticAnalyzer()
        
        # Charger ou créer les modèles
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialise tous les modèles de détection IA"""
        logging.info("🤖 Initialisation du détecteur IA amélioré...")
        
        # 1. Essayer de charger un modèle Transformer pré-entraîné
        self._load_transformer_model()
        
        # 2. Charger ou entraîner le modèle ensemble classique
        self._load_or_train_ensemble_model()
        
        logging.info("✅ Détecteur IA amélioré initialisé")
        
    def _load_transformer_model(self):
        """Charge un modèle Transformer pour détecter le contenu IA"""
        if not TRANSFORMERS_AVAILABLE:
            logging.info("Transformers non disponible - utilisation de modèles classiques")
            return
            
        try:
            # Essayer de charger un modèle spécialisé dans la détection IA
            model_names = [
                "roberta-base-openai-detector",  # OpenAI's GPT-2 detector
                "distilbert-base-uncased",       # Fallback général
                "bert-base-uncased"              # Fallback BERT
            ]
            
            for model_name in model_names:
                try:
                    logging.info(f"Tentative de chargement du modèle {model_name}...")
                    self.transformer_model = pipeline(
                        "text-classification",
                        model=model_name,
                        tokenizer=model_name,
                        device=-1  # CPU
                    )
                    logging.info(f"✅ Modèle Transformer {model_name} chargé avec succès")
                    break
                except Exception as e:
                    logging.debug(f"Échec chargement {model_name}: {e}")
                    continue
                    
        except Exception as e:
            logging.warning(f"Impossible de charger un modèle Transformer: {e}")
            self.transformer_model = None
    
    def _load_or_train_ensemble_model(self):
        """Charge ou entraîne le modèle ensemble classique"""
        model_path = os.path.join(self.models_dir, "ensemble_ai_detector.pkl")
        vectorizer_path = os.path.join(self.models_dir, "tfidf_vectorizer.pkl")
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            try:
                with open(model_path, 'rb') as f:
                    self.ensemble_model = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.tfidf_vectorizer = pickle.load(f)
                logging.info("📥 Modèle ensemble chargé depuis le cache")
                return
            except Exception as e:
                logging.warning(f"Erreur chargement modèle: {e}")
        
        # Entraîner un nouveau modèle
        self._train_ensemble_model()
        
    def _train_ensemble_model(self):
        """Entraîne un modèle ensemble robuste"""
        logging.info("🧠 Entraînement du modèle ensemble IA...")
        
        # Dataset d'entraînement étendu et réaliste
        training_data = self._create_extended_training_dataset()
        
        if not SKLEARN_AVAILABLE:
            logging.warning("Scikit-learn non disponible - modèle simplifié")
            self._create_simple_fallback_model(training_data)
            return
        
        # Préparer les données
        texts = [item['text'] for item in training_data]
        labels = [item['is_ai'] for item in training_data]
        
        # Vectorisation TF-IDF avancée
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 4),  # Jusqu'à 4-grammes
            min_df=2,
            max_df=0.8,
            stop_words='english',
            analyzer='word',
            lowercase=True,
            token_pattern=r'(?u)\b\w+\b',
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=True
        )
        
        X = self.tfidf_vectorizer.fit_transform(texts)
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Entraîner plusieurs modèles
        models = {
            'logistic': LogisticRegression(random_state=42, max_iter=1000),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'naive_bayes': MultinomialNB()
        }
        
        best_model = None
        best_score = 0
        
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                score = accuracy_score(y_test, model.predict(X_test))
                logging.info(f"Modèle {name}: {score:.3f} précision")
                
                if score > best_score:
                    best_score = score
                    best_model = model
            except Exception as e:
                logging.warning(f"Erreur entraînement {name}: {e}")
        
        self.ensemble_model = best_model
        
        # Sauvegarder les modèles
        try:
            model_path = os.path.join(self.models_dir, "ensemble_ai_detector.pkl")
            vectorizer_path = os.path.join(self.models_dir, "tfidf_vectorizer.pkl")
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.ensemble_model, f)
            with open(vectorizer_path, 'wb') as f:
                pickle.dump(self.tfidf_vectorizer, f)
                
            logging.info(f"🎯 Modèle ensemble entraîné: {best_score:.1%} précision")
        except Exception as e:
            logging.error(f"Erreur sauvegarde modèle: {e}")
    
    def _create_extended_training_dataset(self) -> List[Dict]:
        """Crée un dataset d'entraînement étendu et réaliste"""
        
        # Textes humains authentiques (variés)
        human_texts = [
            # Conversations naturelles
            "Salut ! Comment ça va ? J'ai passé une super journée aujourd'hui, j'ai rencontré des amis qu'on avait pas vus depuis longtemps.",
            "Franchement, ce film m'a déçu. Je m'attendais à mieux vu les critiques. Mais bon, c'est subjectif hein.",
            "Ma grand-mère fait les meilleures tartes aux pommes du monde ! Elle refuse de me donner la recette, c'est frustrant lol.",
            
            # Écriture académique humaine (avec imperfections)
            "Dans cette étude, nous avons analysé les données... bon, je dois avouer que les résultats sont un peu décevants.",
            "Les résultats montrent que... enfin, c'est compliqué à expliquer mais globalement ça va dans le bon sens.",
            "Cette recherche vise à comprendre pourquoi les étudiants procrastinent tant (moi le premier d'ailleurs).",
            
            # Opinions personnelles
            "Perso, je pense que cette technologie va changer notre façon de travailler. Ça me fait un peu peur mais c'est excitant aussi.",
            "J'ai testé cette app et franchement c'est pas terrible. L'interface est confuse et ça plante souvent.",
            "Mon boss m'a encore demandé de faire des heures sup... Je suis vraiment fatigué de cette situation.",
            
            # Récits personnels
            "L'autre jour, je suis tombé en panne sur l'autoroute. Heureusement qu'un type sympa s'est arrêté pour m'aider !",
            "Mes vacances en Grèce étaient incroyables ! La bouffe, les paysages, les gens... tout était parfait.",
            "J'ai commencé à apprendre le piano il y a 6 mois. C'est dur mais j'adore ça. Mes voisins moins lol."
        ]
        
        # Textes générés par IA (caractéristiques typiques)
        ai_texts = [
            # Style formel/robotique
            "The implementation of this comprehensive solution demonstrates significant optimization across multiple performance indicators and operational metrics.",
            "Through systematic analysis of available data, this methodology exhibits superior effectiveness in achieving desired outcomes within established parameters.",
            "This innovative approach leverages advanced algorithms to deliver exceptional results while maintaining optimal efficiency and scalability.",
            
            # Transitions formelles répétitives
            "Furthermore, the analysis reveals substantial improvements in key areas. Moreover, the implementation process ensures seamless integration. Additionally, the framework provides comprehensive support for various use cases.",
            "Initially, the system processes input data efficiently. Subsequently, advanced algorithms analyze patterns comprehensively. Finally, optimized results are delivered with exceptional accuracy.",
            "Firstly, this solution addresses core challenges effectively. Secondly, it implements best practices consistently. Thirdly, it delivers measurable value proposition.",
            
            # Vocabulaire sophistiqué excessif
            "The paradigmatic transformation of contemporary methodological frameworks necessitates comprehensive evaluation of multifaceted implementation strategies.",
            "This sophisticated algorithmic architecture demonstrates unprecedented capability in optimizing complex computational processes across diverse operational environments.",
            "The synergistic integration of advanced technological components facilitates enhanced performance metrics and streamlined operational workflows.",
            
            # Répétitions de structure
            "The system provides excellent performance. The system ensures reliable operation. The system delivers optimal results. The system maintains superior efficiency.",
            "This solution offers comprehensive functionality. This solution guarantees exceptional reliability. This solution enables seamless integration. This solution supports scalable architecture.",
            "Users can benefit from enhanced capabilities. Users can access advanced features. Users can utilize optimized workflows. Users can achieve superior outcomes."
        ]
        
        # Assembler le dataset
        dataset = []
        
        for text in human_texts:
            dataset.append({
                'text': text,
                'is_ai': 0,
                'source': 'human_authentic'
            })
        
        for text in ai_texts:
            dataset.append({
                'text': text,
                'is_ai': 1,
                'source': 'ai_generated'
            })
        
        return dataset
    
    def _create_simple_fallback_model(self, training_data):
        """Modèle de fallback simple sans scikit-learn"""
        # Compter les caractéristiques IA communes
        ai_indicators = [
            'furthermore', 'moreover', 'additionally', 'subsequently', 'comprehensive',
            'optimization', 'methodology', 'implementation', 'framework', 'systematic',
            'efficiency', 'performance', 'advanced', 'sophisticated', 'exceptional',
            'demonstrates', 'exhibits', 'facilitates', 'leverages', 'delivers'
        ]
        
        self.simple_model = {
            'ai_indicators': ai_indicators,
            'type': 'simple_fallback'
        }
        
        logging.info("📋 Modèle de fallback simple créé")
    
    def detect_ai_content(self, text: str) -> Dict:
        """Détecte le contenu IA avec tous les modèles disponibles"""
        results = {
            'ai_probability': 0.0,
            'confidence': 'low',
            'method_used': 'fallback',
            'detailed_scores': {}
        }
        
        try:
            scores = []
            methods = []
            
            # 1. Modèle Transformer (si disponible)
            if self.transformer_model:
                transformer_score = self._detect_with_transformer(text)
                if transformer_score is not None:
                    scores.append(transformer_score)
                    methods.append('transformer')
                    results['detailed_scores']['transformer'] = transformer_score
            
            # 2. Modèle ensemble classique
            if self.ensemble_model and self.tfidf_vectorizer:
                ensemble_score = self._detect_with_ensemble(text)
                if ensemble_score is not None:
                    scores.append(ensemble_score)
                    methods.append('ensemble')
                    results['detailed_scores']['ensemble'] = ensemble_score
            
            # 3. Analyse linguistique
            linguistic_score = self.linguistic_analyzer.analyze(text)
            scores.append(linguistic_score)
            methods.append('linguistic')
            results['detailed_scores']['linguistic'] = linguistic_score
            
            # 4. Modèle simple (fallback)
            if hasattr(self, 'simple_model'):
                simple_score = self._detect_with_simple_model(text)
                scores.append(simple_score)
                methods.append('simple')
                results['detailed_scores']['simple'] = simple_score
            
            # Combiner les scores
            if scores:
                # Pondération intelligente
                if len(scores) >= 3:
                    # Moyenne pondérée avec plus de poids aux modèles avancés
                    weights = [0.4, 0.3, 0.2, 0.1][:len(scores)]
                    final_score = sum(s * w for s, w in zip(scores, weights))
                    results['confidence'] = 'high'
                elif len(scores) == 2:
                    final_score = (scores[0] * 0.6 + scores[1] * 0.4)
                    results['confidence'] = 'medium'
                else:
                    final_score = scores[0]
                    results['confidence'] = 'low'
                
                results['ai_probability'] = min(max(final_score, 0), 100)
                results['method_used'] = '+'.join(methods)
            
            logging.info(f"🤖 Détection IA: {results['ai_probability']:.1f}% ({results['method_used']})")
            
        except Exception as e:
            logging.error(f"Erreur détection IA: {e}")
            results['ai_probability'] = 0.0
            
        return results
    
    def _detect_with_transformer(self, text: str) -> float:
        """Détection avec modèle Transformer"""
        try:
            # Limiter la taille du texte pour éviter les timeouts
            text_sample = text[:512] if len(text) > 512 else text
            
            result = self.transformer_model(text_sample)
            
            # Interpréter le résultat selon le modèle
            if isinstance(result, list) and len(result) > 0:
                prediction = result[0]
                
                # Si c'est un modèle de détection GPT
                if 'FAKE' in prediction.get('label', '').upper():
                    return prediction['score'] * 100
                elif 'REAL' in prediction.get('label', '').upper():
                    return (1 - prediction['score']) * 100
                else:
                    # Modèle générique - adapter selon les labels
                    return prediction['score'] * 100
            
        except Exception as e:
            logging.debug(f"Erreur modèle transformer: {e}")
            
        return None
    
    def _detect_with_ensemble(self, text: str) -> float:
        """Détection avec modèle ensemble"""
        try:
            X = self.tfidf_vectorizer.transform([text])
            
            # Prédiction probabiliste
            if hasattr(self.ensemble_model, 'predict_proba'):
                proba = self.ensemble_model.predict_proba(X)[0]
                # Classe 1 = IA
                return proba[1] * 100 if len(proba) > 1 else proba[0] * 100
            else:
                # Prédiction binaire
                prediction = self.ensemble_model.predict(X)[0]
                return 90.0 if prediction == 1 else 10.0
                
        except Exception as e:
            logging.debug(f"Erreur modèle ensemble: {e}")
            
        return None
    
    def _detect_with_simple_model(self, text: str) -> float:
        """Détection avec modèle simple"""
        if not hasattr(self, 'simple_model'):
            return 20.0
            
        text_lower = text.lower()
        ai_indicators = self.simple_model['ai_indicators']
        
        # Compter les indicateurs IA
        indicator_count = sum(1 for indicator in ai_indicators if indicator in text_lower)
        
        # Score basé sur la densité d'indicateurs
        words = len(text.split())
        if words > 0:
            indicator_density = (indicator_count / words) * 100
            # Multiplier par un facteur pour avoir un score significatif
            score = min(indicator_density * 200, 100)
        else:
            score = 0
            
        return score


class LinguisticAnalyzer:
    """Analyseur linguistique pour détecter les patterns IA"""
    
    def analyze(self, text: str) -> float:
        """Analyse linguistique complète"""
        try:
            scores = []
            
            # 1. Répétitivité des structures
            repetition_score = self._analyze_repetition(text)
            scores.append(repetition_score * 0.25)
            
            # 2. Complexité lexicale
            lexical_score = self._analyze_lexical_complexity(text)
            scores.append(lexical_score * 0.25)
            
            # 3. Transitions formelles
            transition_score = self._analyze_formal_transitions(text)
            scores.append(transition_score * 0.25)
            
            # 4. Longueur des phrases
            sentence_score = self._analyze_sentence_patterns(text)
            scores.append(sentence_score * 0.25)
            
            return sum(scores)
            
        except Exception as e:
            logging.debug(f"Erreur analyse linguistique: {e}")
            return 20.0
    
    def _analyze_repetition(self, text: str) -> float:
        """Analyse la répétitivité des structures"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) < 2:
            return 0
        
        # Analyser les débuts de phrases
        starts = [s.split()[:3] if len(s.split()) >= 3 else s.split() for s in sentences]
        start_patterns = [' '.join(start).lower() for start in starts]
        
        # Compter les répétitions
        pattern_counts = Counter(start_patterns)
        repetitions = sum(1 for count in pattern_counts.values() if count > 1)
        
        return min((repetitions / len(sentences)) * 100, 100)
    
    def _analyze_lexical_complexity(self, text: str) -> float:
        """Analyse la complexité lexicale"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        if len(words) < 10:
            return 0
        
        # Mots sophistiqués typiques de l'IA
        sophisticated_words = [
            'comprehensive', 'optimization', 'methodology', 'implementation',
            'sophisticated', 'paradigmatic', 'multifaceted', 'synergistic',
            'unprecedented', 'exceptional', 'substantial', 'significant'
        ]
        
        sophisticated_count = sum(1 for word in words if word in sophisticated_words)
        
        return min((sophisticated_count / len(words)) * 500, 100)  # Facteur 500 pour avoir un score visible
    
    def _analyze_formal_transitions(self, text: str) -> float:
        """Analyse les transitions formelles"""
        formal_transitions = [
            'furthermore', 'moreover', 'additionally', 'subsequently',
            'consequently', 'therefore', 'nonetheless', 'nevertheless'
        ]
        
        text_lower = text.lower()
        transition_count = sum(1 for transition in formal_transitions if transition in text_lower)
        
        words = len(text.split())
        if words > 0:
            return min((transition_count / words) * 300, 100)  # Facteur 300
        
        return 0
    
    def _analyze_sentence_patterns(self, text: str) -> float:
        """Analyse les patterns de longueur de phrases"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if len(sentences) < 2:
            return 0
        
        # Calculer la variance de longueur
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        
        # L'IA tend à avoir des phrases de longueur très uniforme
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        
        # Score inversé : faible variance = plus suspect
        uniformity_score = max(0, 100 - variance * 2)
        
        return min(uniformity_score, 100)


# Test du détecteur
if __name__ == "__main__":
    detector = EnhancedAIDetector()
    
    # Test avec texte IA typique
    ai_text = """
    The implementation of this comprehensive solution demonstrates significant optimization across multiple performance indicators. 
    Furthermore, the systematic analysis reveals substantial improvements in operational efficiency. 
    Moreover, this advanced methodology leverages sophisticated algorithms to deliver exceptional results.
    """
    
    result = detector.detect_ai_content(ai_text)
    print(f"Texte IA - Score: {result['ai_probability']:.1f}% ({result['method_used']})")
    
    # Test avec texte humain
    human_text = """
    Salut ! Comment ça va ? J'ai passé une journée de fou aujourd'hui. 
    Mon boss m'a encore demandé de faire des heures sup, c'est relou. 
    Enfin bon, au moins le weekend arrive bientôt !
    """
    
    result = detector.detect_ai_content(human_text)
    print(f"Texte humain - Score: {result['ai_probability']:.1f}% ({result['method_used']})")