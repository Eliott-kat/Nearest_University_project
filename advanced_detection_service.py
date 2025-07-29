"""
Service de détection avancé utilisant Sentence-BERT et modèles d'IA locaux
Remplace l'algorithme Turnitin par une approche moderne basée sur l'apprentissage automatique
"""

import os
import logging
import pickle
import sqlite3
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Importations conditionnelles pour gérer les dépendances
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import Levenshtein
    LEVENSHTEIN_AVAILABLE = True
except ImportError:
    LEVENSHTEIN_AVAILABLE = False

class AdvancedDetectionService:
    """Service de détection avancé avec Sentence-BERT et modèles d'IA"""
    
    def __init__(self):
        self.sentence_model = None
        self.tfidf_vectorizer = None
        self.ai_detector_model = None
        self.ai_vectorizer = None
        self.local_db_path = "plagiarism_cache/local_documents.db"
        self.models_path = "plagiarism_cache/models"
        
        # Créer les répertoires nécessaires
        os.makedirs("plagiarism_cache", exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        
        # Initialiser les modèles
        self._initialize_models()
        self._setup_local_database()
    
    def _initialize_models(self):
        """Initialise les modèles selon les dépendances disponibles"""
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                logging.info("🤖 Initialisation Sentence-BERT (paraphrase-MiniLM-L6-v2)...")
                try:
                    self.sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
                except Exception as e:
                    logging.warning(f"Impossible de charger Sentence-BERT: {e}")
                    self.sentence_model = None
            else:
                logging.warning("Sentence-transformers non disponible, utilisation d'algorithmes alternatifs")
                self.sentence_model = None
            
            if SKLEARN_AVAILABLE:
                logging.info("📊 Initialisation TF-IDF vectorizer...")
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=5000,
                    stop_words='english',
                    ngram_range=(1, 3),
                    min_df=1
                )
            else:
                logging.warning("Scikit-learn non disponible")
                self.tfidf_vectorizer = None
            
            # Charger ou créer le modèle de détection IA
            self._load_or_create_ai_detector()
            
            logging.info("✅ Modèles initialisés avec dépendances disponibles")
            
        except Exception as e:
            logging.error(f"Erreur initialisation modèles: {e}")
            # Continue avec fonctionnalités limitées
    
    def _setup_local_database(self):
        """Configure la base de données locale pour stocker les documents"""
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    content TEXT,
                    sentences TEXT,  -- JSON des phrases
                    embeddings BLOB,  -- Embeddings Sentence-BERT
                    tfidf_vector BLOB,  -- Vecteur TF-IDF
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT,
                    is_ai_generated INTEGER,  -- 1 for AI, 0 for human
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logging.info("📁 Base de données locale configurée")
            
        except Exception as e:
            logging.error(f"Erreur setup DB: {e}")
    
    def _load_or_create_ai_detector(self):
        """Charge ou crée le modèle de détection IA si les dépendances sont disponibles"""
        if not SKLEARN_AVAILABLE or not JOBLIB_AVAILABLE:
            logging.warning("Dépendances IA non disponibles, utilisation de détection basique")
            self.ai_detector_model = None
            self.ai_vectorizer = None
            return
            
        model_path = os.path.join(self.models_path, "ai_detector.joblib")
        vectorizer_path = os.path.join(self.models_path, "ai_vectorizer.joblib")
        
        try:
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                logging.info("📥 Chargement modèle IA existant...")
                self.ai_detector_model = joblib.load(model_path)
                self.ai_vectorizer = joblib.load(vectorizer_path)
            else:
                logging.info("🔧 Création nouveau modèle de détection IA...")
                self._train_ai_detector()
                
        except Exception as e:
            logging.warning(f"Erreur chargement modèle IA: {e}")
            self._train_ai_detector()
    
    def _train_ai_detector(self):
        """Entraîne le modèle de détection IA avec des données d'exemple"""
        if not SKLEARN_AVAILABLE or not JOBLIB_AVAILABLE:
            self.ai_detector_model = None
            self.ai_vectorizer = None
            return
            
        try:
            # Données d'entraînement d'exemple (à enrichir avec de vraies données)
            human_texts = [
                "Je pense que cette approche est intéressante pour résoudre le problème.",
                "L'analyse des données montre une tendance claire vers l'amélioration.",
                "Mon expérience personnelle me pousse à croire que cette solution fonctionne.",
                "Après réflexion, je recommande cette méthode pour plusieurs raisons pratiques.",
                "Cette recherche m'a permis de comprendre les enjeux complexes du sujet.",
                "Les résultats obtenus correspondent exactement à mes attentes initiales.",
                "Il est important de noter que mes observations diffèrent des études précédentes.",
                "D'après mon point de vue, cette conclusion semble parfaitement justifiée.",
            ]
            
            ai_texts = [
                "Based on the comprehensive analysis of available data, it can be concluded that this methodology demonstrates significant efficacy.",
                "The implementation of this solution presents numerous advantages in terms of efficiency and scalability across multiple domains.",
                "Through systematic evaluation of various parameters, the proposed framework exhibits optimal performance characteristics.",
                "The results indicate a substantial improvement in key performance indicators when utilizing this innovative approach.",
                "This research methodology provides valuable insights into the underlying mechanisms governing the observed phenomena.",
                "The empirical evidence strongly supports the hypothesis that this intervention yields measurable benefits.",
                "Furthermore, the analysis reveals significant correlations between the input variables and the desired outcomes.",
                "In conclusion, the data-driven approach demonstrates superior results compared to traditional methodologies.",
            ]
            
            # Préparer les données d'entraînement
            texts = human_texts + ai_texts
            labels = [0] * len(human_texts) + [1] * len(ai_texts)  # 0=humain, 1=IA
            
            # Vectorisation TF-IDF
            self.ai_vectorizer = TfidfVectorizer(
                max_features=3000,
                ngram_range=(1, 3),
                min_df=1,
                max_df=0.8
            )
            
            X = self.ai_vectorizer.fit_transform(texts)
            
            # Entraînement du modèle
            self.ai_detector_model = LogisticRegression(random_state=42)
            self.ai_detector_model.fit(X, labels)
            
            # Sauvegarder les modèles
            model_path = os.path.join(self.models_path, "ai_detector.joblib")
            vectorizer_path = os.path.join(self.models_path, "ai_vectorizer.joblib")
            
            joblib.dump(self.ai_detector_model, model_path)
            joblib.dump(self.ai_vectorizer, vectorizer_path)
            
            logging.info("🎯 Modèle de détection IA entraîné et sauvegardé")
            
        except Exception as e:
            logging.error(f"Erreur entraînement modèle IA: {e}")
            # Modèle de fallback simple
            self.ai_detector_model = None
            self.ai_vectorizer = None
    
    def detect_plagiarism_and_ai(self, text: str, filename: str = "") -> Dict:
        """Détection complète de plagiat et d'IA avec les modèles avancés"""
        try:
            logging.info("🔍 Démarrage détection avancée (Sentence-BERT + IA)")
            
            # Prétraitement du texte
            sentences = self._split_into_sentences(text)
            
            # Détection de plagiat avec Sentence-BERT
            plagiarism_result = self._detect_similarity_with_bert(text, sentences)
            
            # Détection complémentaire TF-IDF
            tfidf_result = self._detect_similarity_with_tfidf(text)
            
            # Détection Levenshtein pour correspondances exactes
            levenshtein_result = self._detect_exact_matches(text)
            
            # Détection IA
            ai_result = self._detect_ai_content(text, sentences)
            
            # Combiner les résultats
            final_plagiarism_score = max(
                plagiarism_result.get('score', 0),
                tfidf_result.get('score', 0),
                levenshtein_result.get('score', 0)
            )
            
            # Ajuster selon les sources multiples
            if plagiarism_result.get('sources_found', 0) > 0:
                final_plagiarism_score = min(final_plagiarism_score * 1.2, 95)
            
            # Stocker le document dans la base locale
            self._store_document_locally(filename, text, sentences)
            
            result = {
                'percent': round(final_plagiarism_score, 1),
                'sources_found': plagiarism_result.get('sources_found', 0),
                'ai_percent': ai_result.get('ai_probability', 0),
                'details': {
                    'sentence_bert_score': plagiarism_result.get('score', 0),
                    'tfidf_score': tfidf_result.get('score', 0),
                    'levenshtein_score': levenshtein_result.get('score', 0),
                    'ai_sentences': ai_result.get('ai_sentences', 0),
                    'total_sentences': len(sentences)
                },
                'method': 'advanced_sentence_bert_ai_detection'
            }
            
            logging.info(f"🎯 Détection avancée: {final_plagiarism_score}% plagiat + {ai_result.get('ai_probability', 0)}% IA")
            return result
            
        except Exception as e:
            logging.error(f"Erreur détection avancée: {e}")
            # Fallback vers une détection simple
            return {'percent': 0, 'sources_found': 0, 'ai_percent': 0, 'method': 'fallback_error'}
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divise le texte en phrases"""
        import re
        # Regex améliorée pour diviser en phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        return sentences
    
    def _detect_similarity_with_bert(self, text: str, sentences: List[str]) -> Dict:
        """Détection de similarité avec Sentence-BERT (ou méthode alternative)"""
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE or not self.sentence_model or len(sentences) == 0:
                # Fallback vers une méthode basique de comparaison textuelle
                return self._detect_similarity_fallback(text, sentences)
            
            # Encoder les phrases du document actuel
            current_embeddings = self.sentence_model.encode(sentences)
            
            # Comparer avec les documents stockés
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT filename, sentences, embeddings FROM documents")
            
            max_similarity = 0
            sources_found = 0
            
            for row in cursor.fetchall():
                try:
                    stored_filename, stored_sentences_json, stored_embeddings_blob = row
                    
                    if stored_embeddings_blob and NUMPY_AVAILABLE and SKLEARN_AVAILABLE:
                        stored_embeddings = pickle.loads(stored_embeddings_blob)
                        stored_sentences = eval(stored_sentences_json)  # JSON simple
                        
                        # Calculer similarité cosinus entre toutes les phrases
                        similarities = cosine_similarity(current_embeddings, stored_embeddings)
                        
                        # Trouver les meilleures correspondances
                        max_sim = np.max(similarities)
                        if max_sim > 0.7:  # Seuil de similarité élevé
                            max_similarity = max(max_similarity, max_sim * 100)
                            sources_found += 1
                            
                except Exception as e:
                    continue
            
            conn.close()
            
            return {
                'score': min(max_similarity, 100),
                'sources_found': sources_found
            }
            
        except Exception as e:
            logging.error(f"Erreur Sentence-BERT: {e}")
            return {'score': 0, 'sources_found': 0}
    
    def _detect_similarity_fallback(self, text: str, sentences: List[str]) -> Dict:
        """Méthode de fallback pour la détection sans Sentence-BERT"""
        try:
            # Comparaison basique avec correspondance de mots-clés
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM documents")
            
            max_similarity = 0
            sources_found = 0
            text_words = set(text.lower().split())
            
            for row in cursor.fetchall():
                stored_text = row[0]
                stored_words = set(stored_text.lower().split())
                
                # Calcul de similarité Jaccard
                intersection = len(text_words.intersection(stored_words))
                union = len(text_words.union(stored_words))
                
                if union > 0:
                    similarity = (intersection / union) * 100
                    if similarity > 30:  # Seuil plus bas pour méthode basique
                        max_similarity = max(max_similarity, similarity)
                        sources_found += 1
            
            conn.close()
            return {'score': max_similarity, 'sources_found': sources_found}
            
        except Exception as e:
            logging.error(f"Erreur fallback: {e}")
            return {'score': 0, 'sources_found': 0}
    
    def _detect_similarity_with_tfidf(self, text: str) -> Dict:
        """Détection rapide avec TF-IDF (si disponible)"""
        try:
            if not SKLEARN_AVAILABLE or not self.tfidf_vectorizer:
                return {'score': 0}
                
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM documents")
            
            stored_texts = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if not stored_texts:
                return {'score': 0}
            
            # Ajouter le texte actuel pour comparaison
            all_texts = stored_texts + [text]
            
            # Vectorisation TF-IDF
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Calculer similarité avec le dernier document (texte actuel)
            current_vector = tfidf_matrix[-1]
            similarities = cosine_similarity(current_vector, tfidf_matrix[:-1])
            
            max_similarity = np.max(similarities) if similarities.size > 0 and NUMPY_AVAILABLE else 0
            
            return {'score': max_similarity * 100}
            
        except Exception as e:
            logging.error(f"Erreur TF-IDF: {e}")
            return {'score': 0}
    
    def _detect_exact_matches(self, text: str) -> Dict:
        """Détection de correspondances exactes avec Levenshtein (ou méthode alternative)"""
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM documents")
            
            max_similarity = 0
            
            for row in cursor.fetchall():
                stored_text = row[0]
                
                if LEVENSHTEIN_AVAILABLE:
                    # Calculer distance Levenshtein
                    distance = Levenshtein.distance(text.lower(), stored_text.lower())
                    max_length = max(len(text), len(stored_text))
                    
                    if max_length > 0:
                        similarity = (1 - distance / max_length) * 100
                        max_similarity = max(max_similarity, similarity)
                else:
                    # Méthode alternative : pourcentage de correspondance de caractères
                    text_lower = text.lower()
                    stored_lower = stored_text.lower()
                    
                    # Compter les sous-chaînes communes
                    common_chars = 0
                    for i in range(min(len(text_lower), len(stored_lower))):
                        if text_lower[i] == stored_lower[i]:
                            common_chars += 1
                    
                    max_length = max(len(text), len(stored_text))
                    if max_length > 0:
                        similarity = (common_chars / max_length) * 100
                        max_similarity = max(max_similarity, similarity)
            
            conn.close()
            
            return {'score': max_similarity}
            
        except Exception as e:
            logging.error(f"Erreur détection exacte: {e}")
            return {'score': 0}
    
    def _detect_ai_content(self, text: str, sentences: List[str]) -> Dict:
        """Détection de contenu généré par IA"""
        try:
            if not self.ai_detector_model or not self.ai_vectorizer:
                return {'ai_probability': 0, 'ai_sentences': 0}
            
            ai_sentences = 0
            total_sentences = len(sentences)
            
            for sentence in sentences:
                if len(sentence.strip()) < 20:  # Ignorer phrases trop courtes
                    continue
                
                # Vectoriser la phrase
                sentence_vector = self.ai_vectorizer.transform([sentence])
                
                # Prédire si c'est de l'IA
                ai_probability = self.ai_detector_model.predict_proba(sentence_vector)[0][1]
                
                if ai_probability > 0.6:  # Seuil de confiance
                    ai_sentences += 1
            
            overall_ai_probability = 0
            if total_sentences > 0:
                overall_ai_probability = (ai_sentences / total_sentences) * 100
            
            return {
                'ai_probability': round(overall_ai_probability, 1),
                'ai_sentences': ai_sentences
            }
            
        except Exception as e:
            logging.error(f"Erreur détection IA: {e}")
            return {'ai_probability': 0, 'ai_sentences': 0}
    
    def _store_document_locally(self, filename: str, text: str, sentences: List[str]):
        """Stocke le document dans la base locale pour futures comparaisons"""
        try:
            embeddings_blob = None
            
            # Encoder les phrases avec Sentence-BERT si disponible
            if self.sentence_model and SENTENCE_TRANSFORMERS_AVAILABLE:
                embeddings = self.sentence_model.encode(sentences)
                embeddings_blob = pickle.dumps(embeddings)
            
            # Sérialiser les données
            sentences_json = str(sentences)  # Simple serialization
            
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO documents (filename, content, sentences, embeddings)
                VALUES (?, ?, ?, ?)
            ''', (filename, text, sentences_json, embeddings_blob))
            
            conn.commit()
            conn.close()
            
            logging.info(f"📚 Document '{filename}' ajouté à la base locale")
            
        except Exception as e:
            logging.error(f"Erreur stockage document: {e}")

# Instance globale du service
advanced_detection_service = None

def get_advanced_detection_service():
    """Retourne l'instance du service de détection avancé"""
    global advanced_detection_service
    if advanced_detection_service is None:
        advanced_detection_service = AdvancedDetectionService()
    return advanced_detection_service