"""
Implémentation complète du système de détection avancé avec Sentence-BERT
Inclut TF-IDF, cosine similarity, Levenshtein distance et modèle IA local
"""

import os
import logging
import pickle
import sqlite3
import re
import json
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import Counter, defaultdict

# Import du détecteur GPTZero-like
try:
    from utils.ai_gptzero_like import detect_ai_gptzero_like
    GPTZERO_AVAILABLE = True
    logging.info("✅ Détecteur GPTZero-like chargé avec succès")
except ImportError as e:
    GPTZERO_AVAILABLE = False
    logging.warning(f"⚠️ Détecteur GPTZero non disponible: {e}")

class ManualTfIdf:
    """Implémentation manuelle de TF-IDF"""
    
    def __init__(self, max_features=5000, ngram_range=(1, 3)):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vocabulary = {}
        self.idf_values = {}
        self.documents = []
    
    def _extract_ngrams(self, text, n):
        """Extrait les n-grammes d'un texte"""
        words = text.lower().split()
        if n == 1:
            return words
        return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
    
    def _get_all_ngrams(self, text):
        """Obtient tous les n-grammes selon ngram_range"""
        all_ngrams = []
        for n in range(self.ngram_range[0], self.ngram_range[1] + 1):
            all_ngrams.extend(self._extract_ngrams(text, n))
        return all_ngrams
    
    def fit_transform(self, texts):
        """Entraîne le modèle et transforme les textes"""
        self.documents = texts
        
        # Construire le vocabulaire
        all_terms = []
        doc_term_counts = []
        
        for text in texts:
            terms = self._get_all_ngrams(text)
            term_counts = Counter(terms)
            doc_term_counts.append(term_counts)
            all_terms.extend(terms)
        
        # Créer vocabulaire avec les termes les plus fréquents
        term_freq = Counter(all_terms)
        vocab_terms = [term for term, _ in term_freq.most_common(self.max_features)]
        self.vocabulary = {term: idx for idx, term in enumerate(vocab_terms)}
        
        # Calculer IDF
        num_docs = len(texts)
        for term in self.vocabulary:
            doc_count = sum(1 for doc_counts in doc_term_counts if term in doc_counts)
            self.idf_values[term] = math.log(num_docs / max(1, doc_count))
        
        # Créer matrice TF-IDF
        tfidf_matrix = []
        for doc_counts in doc_term_counts:
            doc_vector = [0.0] * len(self.vocabulary)
            doc_length = sum(doc_counts.values())
            
            for term, tf in doc_counts.items():
                if term in self.vocabulary:
                    term_idx = self.vocabulary[term]
                    tf_score = tf / max(1, doc_length)
                    idf_score = self.idf_values[term]
                    doc_vector[term_idx] = tf_score * idf_score
            
            tfidf_matrix.append(doc_vector)
        
        return tfidf_matrix
    
    def transform(self, texts):
        """Transforme de nouveaux textes avec le modèle entraîné"""
        tfidf_matrix = []
        
        for text in texts:
            terms = self._get_all_ngrams(text)
            term_counts = Counter(terms)
            doc_vector = [0.0] * len(self.vocabulary)
            doc_length = sum(term_counts.values())
            
            for term, tf in term_counts.items():
                if term in self.vocabulary:
                    term_idx = self.vocabulary[term]
                    tf_score = tf / max(1, doc_length)
                    idf_score = self.idf_values.get(term, 0)
                    doc_vector[term_idx] = tf_score * idf_score
            
            tfidf_matrix.append(doc_vector)
        
        return tfidf_matrix

def cosine_similarity_manual(vec1, vec2):
    """Calcul manuel de la similarité cosinus"""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)

def levenshtein_distance_manual(s1, s2):
    """Calcul manuel de la distance de Levenshtein optimisé pour gros documents"""
    # OPTIMISATION: Limiter la taille pour éviter les timeouts
    MAX_LEN = 1000  # Limite à 1000 caractères par string
    
    if len(s1) > MAX_LEN:
        s1 = s1[:MAX_LEN//2] + s1[-MAX_LEN//2:]
    if len(s2) > MAX_LEN:
        s2 = s2[:MAX_LEN//2] + s2[-MAX_LEN//2:]
    
    if len(s1) < len(s2):
        return levenshtein_distance_manual(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    # OPTIMISATION: Early exit si très différentes
    if abs(len(s1) - len(s2)) > min(len(s1), len(s2)) * 0.8:
        return max(len(s1), len(s2))  # Très différentes
    
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        
        # OPTIMISATION: Early exit si distance devient trop grande
        if i > 100 and min(current_row) > len(s2) * 0.5:
            return len(s1)  # Distance trop grande, abandon
    
    return previous_row[-1]

class SimpleEmbedding:
    """Embeddings simplifiés basés sur TF-IDF pour simuler Sentence-BERT"""
    
    def __init__(self):
        self.tfidf = ManualTfIdf(max_features=300, ngram_range=(1, 2))
        self.is_fitted = False
    
    def encode(self, sentences):
        """Encode les phrases en vecteurs"""
        if not self.is_fitted:
            # Premier passage pour entraîner le modèle
            self.tfidf.fit_transform(sentences)
            self.is_fitted = True
            return self.tfidf.transform(sentences)
        else:
            return self.tfidf.transform(sentences)

class ManualLogisticRegression:
    """Implémentation basique de régression logistique"""
    
    def __init__(self):
        self.weights = None
        self.bias = 0
    
    def _sigmoid(self, z):
        """Fonction sigmoïde"""
        return 1 / (1 + math.exp(-max(-250, min(250, z))))
    
    def fit(self, X, y, learning_rate=0.01, epochs=100):
        """Entraîne le modèle"""
        n_features = len(X[0]) if X else 0
        self.weights = [0.0] * n_features
        self.bias = 0
        
        for epoch in range(epochs):
            for i, features in enumerate(X):
                # Prédiction
                z = sum(w * f for w, f in zip(self.weights, features)) + self.bias
                prediction = self._sigmoid(z)
                
                # Calcul erreur
                error = y[i] - prediction
                
                # Mise à jour des poids
                for j in range(n_features):
                    self.weights[j] += learning_rate * error * features[j]
                self.bias += learning_rate * error
    
    def predict_proba(self, X):
        """Prédit les probabilités"""
        results = []
        for features in X:
            if self.weights is None:
                return [[0.5, 0.5] for _ in X]
            z = sum(w * f for w, f in zip(self.weights, features)) + self.bias
            prob = self._sigmoid(z)
            results.append([1 - prob, prob])  # [prob_class_0, prob_class_1]
        return results

class SentenceBertDetectionService:
    """Service de détection avancé avec implémentation complète"""
    
    def __init__(self):
        self.embedding_model = SimpleEmbedding()
        self.tfidf_model = ManualTfIdf()
        self.ai_detector = ManualLogisticRegression()
        self.ai_tfidf = ManualTfIdf(max_features=1000, ngram_range=(1, 2))
        
        self.local_db_path = "plagiarism_cache/sentence_bert_db.db"
        self.models_path = "plagiarism_cache/models"
        
        os.makedirs("plagiarism_cache", exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        
        self._setup_database()
        self._train_ai_detector()
        
        logging.info("✅ Système Sentence-BERT manuel initialisé avec succès")
    
    def _setup_database(self):
        """Configure la base de données"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                content TEXT,
                sentences TEXT,
                embeddings TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _train_ai_detector(self):
        """Entraîne le détecteur IA avec données étendues"""
        # Textes humains (style naturel, personnel)
        human_texts = [
            "Je pense que cette approche est vraiment intéressante et j'aimerais l'explorer davantage.",
            "Mon expérience personnelle me dit que cette solution pourrait fonctionner dans notre contexte.",
            "Après avoir réfléchi longuement, je crois que nous devrions essayer cette méthode.",
            "Cette recherche m'a fait comprendre les enjeux complexes derrière ce problème.",
            "D'après ce que j'ai observé, les résultats sont plutôt encourageants pour l'avenir.",
            "Il me semble que cette conclusion est logique compte tenu des données disponibles.",
            "Personnellement, je trouve que cette analyse apporte un éclairage nouveau sur la question.",
            "Mon point de vue sur cette question a évolué après avoir lu ces travaux.",
            "Je recommande vivement cette approche basée sur mon expérience pratique.",
            "Cette méthode me paraît prometteuse pour résoudre notre problème actuel."
        ]
        
        # Textes IA (style formel, répétitif, vocabulaire technique)
        ai_texts = [
            "Based on comprehensive analysis of available data, this methodology demonstrates significant efficacy.",
            "The implementation of this solution presents numerous advantages in terms of efficiency and scalability.",
            "Through systematic evaluation of various parameters, the proposed framework exhibits optimal performance.",
            "The results indicate substantial improvement in key performance indicators when utilizing this approach.",
            "This research methodology provides valuable insights into the underlying mechanisms governing the phenomena.",
            "The empirical evidence strongly supports the hypothesis that this intervention yields measurable benefits.",
            "Furthermore, the analysis reveals significant correlations between input variables and desired outcomes.",
            "In conclusion, the data-driven approach demonstrates superior results compared to traditional methodologies.",
            "The proposed framework leverages advanced algorithms to optimize performance across multiple dimensions.",
            "Subsequently, the implementation of this solution facilitates enhanced operational efficiency and effectiveness."
        ]
        
        # Préparer données d'entraînement
        all_texts = human_texts + ai_texts
        labels = [0] * len(human_texts) + [1] * len(ai_texts)  # 0=humain, 1=IA
        
        # Entraîner le vectoriseur
        X = self.ai_tfidf.fit_transform(all_texts)
        
        # Entraîner le classificateur
        self.ai_detector.fit(X, labels)
        
        logging.info("🧠 Modèle de détection IA entraîné sur données étendues")
    
    def detect_plagiarism_and_ai(self, text: str, filename: str = "") -> Dict:
        """Détection complète avec Sentence-BERT, TF-IDF et Levenshtein"""
        try:
            logging.info("🔍 Démarrage détection Sentence-BERT complète")
            
            # Diviser en phrases
            sentences = self._split_into_sentences(text)
            
            # 1. Détection avec embeddings (Sentence-BERT simulé)
            bert_result = self._detect_with_sentence_bert(text, sentences)
            
            # 2. Détection TF-IDF + Cosine similarity
            tfidf_result = self._detect_with_tfidf_cosine(text)
            
            # 3. Détection Levenshtein
            levenshtein_result = self._detect_with_levenshtein(text)
            
            # 4. Détection IA
            ai_result = self._detect_ai_content(text, sentences)
            
            # NOUVEAU: Détection de contenu académique légitime
            is_academic = self._is_academic_content(text)
            
            # Combiner les scores avec ajustement pour contenu académique
            bert_score = bert_result.get('score', 0)
            tfidf_score = tfidf_result.get('score', 0)
            levenshtein_score = levenshtein_result.get('score', 0)
            
            # Réduire sensibilité pour contenu académique
            if is_academic:
                bert_score *= 0.5  # Réduction plus forte de 50%
                tfidf_score *= 0.6  # Réduction plus forte de 40%
                levenshtein_score *= 0.7  # Réduction plus forte de 30%
                logging.info("📚 Contenu académique détecté - ajustement des scores")
            
            # Pondération améliorée
            final_score = max(
                bert_score * 0.4,      # Réduction de 50% → 40%
                tfidf_score * 0.35,    # Augmentation 30% → 35%
                levenshtein_score * 0.25  # Augmentation 20% → 25%
            )
            
            # Bonus si multiple méthodes détectent (seuils plus élevés)
            detection_count = sum([
                1 if bert_score > 15 else 0,    # Seuil augmenté 10 → 15
                1 if tfidf_score > 15 else 0,   # Seuil augmenté 10 → 15
                1 if levenshtein_score > 20 else 0  # Seuil augmenté 10 → 20
            ])
            
            # Bonus réduit pour éviter sur-détection
            if detection_count >= 2:
                bonus_factor = 1.15 if is_academic else 1.25  # Bonus réduit pour académique
                final_score = min(final_score * bonus_factor, 90)  # Limite abaissée 95 → 90
            
            # Stocker le document
            self._store_document(filename, text, sentences)
            
            result = {
                'percent': round(final_score, 1),
                'sources_found': bert_result.get('sources', 0) + tfidf_result.get('sources', 0),
                'ai_percent': ai_result.get('ai_probability', 0),
                'details': {
                    'sentence_bert_score': bert_result.get('score', 0),
                    'tfidf_cosine_score': tfidf_result.get('score', 0),
                    'levenshtein_score': levenshtein_result.get('score', 0),
                    'detection_methods': detection_count,
                    'ai_sentences': ai_result.get('ai_sentences', 0),
                    'total_sentences': len(sentences)
                },
                'method': 'sentence_bert_tfidf_levenshtein_ai_complete'
            }
            
            logging.info(f"🎯 Détection complète: {final_score}% plagiat + {ai_result.get('ai_probability', 0)}% IA")
            return result
            
        except Exception as e:
            logging.error(f"Erreur détection complète: {e}")
            return {'percent': 0, 'sources_found': 0, 'ai_percent': 0, 'method': 'error'}
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divise en phrases"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 15]
    
    def _is_academic_content(self, text: str) -> bool:
        """Détecte si le contenu est académique/thèse légitime"""
        try:
            text_lower = text.lower()
            
            # Indicateurs de contenu académique
            academic_indicators = [
                'thesis', 'dissertation', 'abstract', 'methodology', 'literature review',
                'chapter', 'introduction', 'conclusion', 'references', 'bibliography',
                'university', 'institute', 'department', 'supervisor', 'professor',
                'master', 'phd', 'degree', 'research', 'study', 'analysis',
                'acknowledgments', 'declaration', 'approved by', 'examining committee',
                'empirical findings', 'theoretical framework', 'data analysis',
                'regression', 'econometric', 'panel data', 'statistical significance'
            ]
            
            # Patterns de thèse/mémoire
            thesis_patterns = [
                r'master.{0,20}thesis', r'phd.{0,20}dissertation', r'research.{0,20}question',
                r'chapter.{0,5}[ivx\d]+', r'table.{0,5}of.{0,5}contents',
                r'approved.{0,20}by', r'examining.{0,20}committee',
                r'empirical.{0,20}findings', r'literature.{0,20}review'
            ]
            
            # Compter indicateurs
            indicator_count = sum(1 for indicator in academic_indicators if indicator in text_lower)
            pattern_count = sum(1 for pattern in thesis_patterns if re.search(pattern, text_lower))
            
            # Structure académique (chapitres, sections)
            has_chapters = bool(re.search(r'chapter\s+[ivx\d]+', text_lower))
            has_abstract = 'abstract' in text_lower
            has_references = any(word in text_lower for word in ['references', 'bibliography', 'works cited'])
            
            # Score académique
            academic_score = indicator_count + (pattern_count * 2)
            if has_chapters: academic_score += 3
            if has_abstract: academic_score += 2
            if has_references: academic_score += 2
            
            is_academic = academic_score >= 8  # Seuil pour considérer comme académique
            
            if is_academic:
                logging.info(f"📚 Contenu académique identifié (score: {academic_score})")
            
            return is_academic
            
        except Exception as e:
            logging.error(f"Erreur détection académique: {e}")
            return False
    
    def _detect_with_sentence_bert(self, text: str, sentences: List[str]) -> Dict:
        """Détection avec embeddings de phrases"""
        try:
            if not sentences:
                return {'score': 0, 'sources': 0}
            
            # Encoder les phrases actuelles
            current_embeddings = self.embedding_model.encode(sentences)
            
            # Comparer avec documents stockés
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT content, sentences, embeddings FROM documents")
            
            max_similarity = 0
            sources_found = 0
            
            for row in cursor.fetchall():
                try:
                    stored_content, stored_sentences_json, stored_embeddings_json = row
                    
                    if stored_embeddings_json:
                        stored_sentences = json.loads(stored_sentences_json)
                        stored_embeddings = json.loads(stored_embeddings_json)
                        
                        # Comparer chaque phrase actuelle avec chaque phrase stockée
                        for curr_emb in current_embeddings:
                            for stored_emb in stored_embeddings:
                                similarity = cosine_similarity_manual(curr_emb, stored_emb)
                                if similarity > 0.75:  # Seuil élevé pour similarité sémantique
                                    max_similarity = max(max_similarity, similarity * 100)
                                    if similarity > 0.85:
                                        sources_found += 1
                
                except (json.JSONDecodeError, Exception):
                    continue
            
            conn.close()
            
            return {
                'score': min(max_similarity, 100),
                'sources': min(sources_found, 10)
            }
            
        except Exception as e:
            logging.error(f"Erreur Sentence-BERT: {e}")
            return {'score': 0, 'sources': 0}
    
    def _detect_with_tfidf_cosine(self, text: str) -> Dict:
        """Détection TF-IDF + cosine similarity"""
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM documents")
            
            stored_texts = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if not stored_texts:
                return {'score': 0, 'sources': 0}
            
            # Transformer tous les textes
            all_texts = stored_texts + [text]
            tfidf_vectors = self.tfidf_model.fit_transform(all_texts)
            
            # Comparer le dernier (texte actuel) avec les autres
            current_vector = tfidf_vectors[-1]
            max_similarity = 0
            sources_found = 0
            
            for i, stored_vector in enumerate(tfidf_vectors[:-1]):
                similarity = cosine_similarity_manual(current_vector, stored_vector)
                if similarity > 0.35:  # Seuil augmenté 0.3 → 0.35 pour réduire false positives
                    max_similarity = max(max_similarity, similarity * 100)
                    if similarity > 0.6:  # Seuil augmenté 0.5 → 0.6 pour sources
                        sources_found += 1
            
            return {
                'score': max_similarity,
                'sources': sources_found
            }
            
        except Exception as e:
            logging.error(f"Erreur TF-IDF: {e}")
            return {'score': 0, 'sources': 0}
    
    def _detect_with_levenshtein(self, text: str) -> Dict:
        """Détection avec distance de Levenshtein optimisée pour gros documents"""
        try:
            # OPTIMISATION: Limiter la taille du texte d'entrée
            if len(text) > 2000:
                text = text[:1000] + text[-1000:]  # Prendre début et fin
                logging.info(f"📝 Texte tronqué pour optimisation Levenshtein")
            
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM documents LIMIT 50")  # Limiter le nombre de comparaisons
            
            max_similarity = 0
            comparisons = 0
            
            for row in cursor.fetchall():
                stored_text = row[0]
                if not stored_text or len(stored_text) < 20:
                    continue
                
                # OPTIMISATION: Pré-filtre rapide avec mots communs
                text_words = set(text.lower().split()[:50])  # Premiers 50 mots
                stored_words = set(stored_text.lower().split()[:50])
                common_ratio = len(text_words & stored_words) / max(len(text_words), 1)
                
                # Skip si très peu de mots communs (seuil augmenté)
                if common_ratio < 0.15:  # Augmenté 0.1 → 0.15 pour réduire comparaisons
                    continue
                
                # Calculer distance Levenshtein seulement si prometteur
                distance = levenshtein_distance_manual(text.lower(), stored_text.lower())
                max_length = max(len(text), len(stored_text))
                
                if max_length > 0:
                    similarity = (1 - distance / max_length) * 100
                    max_similarity = max(max_similarity, similarity)
                
                comparisons += 1
                
                # OPTIMISATION: Stop si très bonne correspondance trouvée
                if max_similarity > 95 or comparisons > 20:  # Limite à 20 comparaisons
                    break
            
            conn.close()
            logging.debug(f"Levenshtein: {comparisons} comparaisons, max: {max_similarity:.1f}%")
            
            return {'score': max_similarity}
            
        except Exception as e:
            logging.error(f"Erreur Levenshtein: {e}")
            return {'score': 0}
    
    def _detect_ai_content(self, text: str, sentences: List[str]) -> Dict:
        """Détection de contenu IA ultra-avancée avec 7 couches d'analyse"""
        try:
            if not sentences:
                return {'ai_probability': 0, 'ai_sentences': 0}
            
            ai_sentences = 0
            total_sentences = len(sentences)
            ai_scores = []
            
            # 1. MOTS-CLÉS IA ÉTENDUS (catégorisés par domaine) - AJUSTÉS pour académique
            ai_keywords_academic = [
                'optimal solution', 'leverages advanced', 'state-of-the-art implementation',
                'cutting-edge methodology', 'revolutionary approach', 'unprecedented results',
                'groundbreaking analysis', 'innovative framework', 'disruptive technology',
                'paradigm-shifting', 'next-generation solution'  # Réduit les mots académiques normaux
            ]
            
            ai_keywords_business = [
                'strategic advantage', 'optimization', 'stakeholders', 'deliverables',
                'synergies', 'best practices', 'core competencies', 'value proposition',
                'scalability', 'paradigm', 'innovative solutions', 'cutting-edge',
                'state-of-the-art', 'industry-leading', 'next-generation'
            ]
            
            ai_keywords_technical = [
                'algorithm', 'utilize', 'implement', 'architecture', 'infrastructure',
                'deployment', 'configuration', 'integration', 'optimization',
                'automated', 'machine learning', 'artificial intelligence', 'deep learning'
            ]
            
            # 2. PATTERNS LINGUISTIQUES AVANCÉS
            ai_patterns_advanced = [
                r'based on .+ analysis', r'the .+ demonstrates', r'furthermore.+',
                r'subsequently.+', r'the empirical evidence', r'in conclusion.+',
                r'the proposed .+ exhibits', r'through systematic', r'it is important to note',
                r'this approach ensures', r'the implementation of', r'as a result of',
                r'in order to .+ it is .+', r'the utilization of', r'with regard to'
            ]
            
            # 3. STRUCTURES SYNTAXIQUES IA
            ai_syntax_patterns = [
                r'the .+ of .+ is .+ by', r'in .+ to .+ the .+',
                r'through the use of', r'by means of', r'in accordance with',
                r'with respect to', r'in terms of', r'as it relates to'
            ]
            
            # 4. INDICATEURS STYLISTIQUES FORMELS
            formal_transitions = [
                'therefore', 'however', 'moreover', 'nevertheless', 'consequently',
                'additionally', 'furthermore', 'nonetheless', 'thus', 'hence',
                'accordingly', 'conversely', 'similarly', 'alternatively'
            ]
            
            # 5. DÉTECTION DE RÉPÉTITIONS SUSPECTES
            sentence_beginnings = [s.split()[:3] for s in sentences if len(s.split()) >= 3]
            repetitive_starts = len(sentence_beginnings) - len(set([' '.join(start) for start in sentence_beginnings]))
            
            for sentence in sentences:
                sentence_lower = sentence.lower().strip()
                if len(sentence_lower) < 20:
                    continue
                
                ai_score = 0
                
                # COUCHE 1: Modèle ML (35%)
                try:
                    sentence_vector = self.ai_tfidf.transform([sentence])[0]
                    probabilities = self.ai_detector.predict_proba([sentence_vector])[0]
                    ml_score = probabilities[1] * 100
                    ai_score += ml_score * 0.35
                except:
                    ml_score = 0
                
                # COUCHE 2: Mots-clés académiques (20%)
                academic_count = sum(1 for keyword in ai_keywords_academic if keyword in sentence_lower)
                academic_score = min(academic_count * 20, 100)
                ai_score += academic_score * 0.2
                
                # COUCHE 3: Mots-clés business/technique (15%)
                business_count = sum(1 for keyword in ai_keywords_business if keyword in sentence_lower)
                tech_count = sum(1 for keyword in ai_keywords_technical if keyword in sentence_lower)
                combined_score = min((business_count + tech_count) * 15, 100)
                ai_score += combined_score * 0.15
                
                # COUCHE 4: Patterns linguistiques avancés (10%)
                pattern_matches = sum(1 for pattern in ai_patterns_advanced + ai_syntax_patterns 
                                    if re.search(pattern, sentence_lower))
                pattern_score = min(pattern_matches * 25, 100)
                ai_score += pattern_score * 0.1
                
                # COUCHE 5: Transitions formelles (8%)
                formal_count = sum(1 for indicator in formal_transitions if indicator in sentence_lower)
                formal_score = min(formal_count * 20, 100)
                ai_score += formal_score * 0.08
                
                # COUCHE 6: Analyse de longueur de phrase (7%)
                words = sentence.split()
                if len(words) > 25:  # Phrases très longues = style IA
                    length_score = min((len(words) - 25) * 3, 100)
                    ai_score += length_score * 0.07
                
                # COUCHE 7: Détection de vocabulaire sophistiqué (5%)
                sophisticated_words = [
                    'utilization', 'implementation', 'optimization', 'enhancement',
                    'facilitation', 'consideration', 'demonstration', 'evaluation',
                    'establishment', 'development', 'achievement', 'improvement'
                ]
                sophisticated_count = sum(1 for word in sophisticated_words if word in sentence_lower)
                sophisticated_score = min(sophisticated_count * 30, 100)
                ai_score += sophisticated_score * 0.05
                
                # BONUS: Répétitions suspectes de structures
                if repetitive_starts > total_sentences * 0.3:
                    ai_score *= 1.15
                
                # BONUS: Absence totale de pronoms personnels (très suspect)
                personal_pronouns = ['i ', 'me ', 'my ', 'we ', 'us ', 'our ', 'you ', 'your ']
                if not any(pronoun in sentence_lower for pronoun in personal_pronouns):
                    ai_score *= 1.1
                
                # Score final pour cette phrase
                final_sentence_score = min(ai_score, 100)
                ai_scores.append(final_sentence_score)
                
                # Seuil de détection IA adaptatif et plus strict
                is_academic = self._is_academic_content(text)
                if is_academic:
                    threshold = 50 if len(sentence.split()) > 20 else 60  # Seuils plus élevés pour académique
                else:
                    threshold = 40 if len(sentence.split()) > 20 else 50  # Seuils normaux
                
                if final_sentence_score > threshold:
                    ai_sentences += 1
                    logging.debug(f"Phrase IA détectée ({final_sentence_score:.1f}%): {sentence[:80]}...")
            
            # Calcul score global avec ajustement pour contenu académique
            if ai_scores:
                base_score = sum(ai_scores) / len(ai_scores)
                
                # Réduction pour contenu académique légitime
                is_academic = self._is_academic_content(text)
                if is_academic:
                    base_score *= 0.5  # Réduction plus forte (-50%) pour thèses légitimes
                    logging.info("📚 Ajustement IA pour contenu académique (-50%)")
                
                # BONUS GLOBAL réduit: Cohérence stylistique
                score_variance = sum((score - base_score) ** 2 for score in ai_scores) / len(ai_scores)
                if score_variance < 50:  # Seuil plus strict (100→50)
                    variance_bonus = 1.1 if is_academic else 1.15  # Bonus réduit pour académique
                    base_score *= variance_bonus
                
                # BONUS GLOBAL réduit: Proportion de phrases détectées
                detection_ratio = ai_sentences / total_sentences
                if detection_ratio > 0.7:  # Seuil plus élevé (0.6→0.7)
                    ratio_bonus = 1.1 if is_academic else 1.2  # Bonus réduit pour académique
                    base_score *= ratio_bonus
                elif detection_ratio > 0.5:  # Seuil plus élevé (0.4→0.5)
                    ratio_bonus = 1.05 if is_academic else 1.1
                    base_score *= ratio_bonus
                
                overall_ai_prob = min(base_score, 100)
            else:
                overall_ai_prob = 0
            
            logging.info(f"🤖 Détection IA AVANCÉE: {ai_sentences}/{total_sentences} phrases = {overall_ai_prob:.1f}%")
            
            # COUCHE 8: Intégration GPTZero (perplexité + burstiness)
            gptzero_bonus = 0
            gptzero_result = None
            try:
                from utils.ai_gptzero_like import detect_ai_gptzero_like, GPTZERO_AVAILABLE
                if GPTZERO_AVAILABLE:
                    try:
                        gptzero_result = detect_ai_gptzero_like(text)
                        if gptzero_result['is_ai']:
                            # Bonus adaptatif basé sur nombre d'indicateurs détectés
                            indicator_multiplier = min(gptzero_result.get('indicators_detected', 1) / 7, 1)
                            gptzero_bonus = gptzero_result['confidence'] * 0.4 * indicator_multiplier  # Max 40% du score GPTZero
                            overall_ai_prob = min(overall_ai_prob + gptzero_bonus, 100)
                            logging.info(f"🔍 GPTZero ULTRA: {gptzero_result['confidence']}% IA ({gptzero_result.get('indicators_detected', 0)} indicateurs - P={gptzero_result['perplexity']}, B={gptzero_result['burstiness']})")
                        else:
                            logging.info(f"🔍 GPTZero: {gptzero_result['confidence']}% (P={gptzero_result['perplexity']}, B={gptzero_result['burstiness']}) - Humain détecté")
                    except Exception as e:
                        logging.error(f"Erreur GPTZero: {e}")
            except ImportError:
                logging.debug("GPTZero non disponible")
            
            return {
                'ai_probability': round(overall_ai_prob, 1),
                'ai_sentences': ai_sentences,
                'total_analyzed': total_sentences,
                'detection_details': {
                    'repetitive_structures': repetitive_starts,
                    'avg_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
                    'formal_ratio': detection_ratio,
                    'gptzero_bonus': round(gptzero_bonus, 1)
                },
                'gptzero_analysis': gptzero_result
            }
            
        except Exception as e:
            logging.error(f"Erreur détection IA: {e}")
            return {'ai_probability': 0, 'ai_sentences': 0}
    
    def _store_document(self, filename: str, text: str, sentences: List[str]):
        """Stocke le document avec embeddings"""
        try:
            # Générer embeddings
            embeddings = self.embedding_model.encode(sentences)
            
            # Sérialiser en JSON
            sentences_json = json.dumps(sentences)
            embeddings_json = json.dumps(embeddings)
            
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO documents (filename, content, sentences, embeddings)
                VALUES (?, ?, ?, ?)
            ''', (filename, text, sentences_json, embeddings_json))
            
            conn.commit()
            conn.close()
            
            logging.info(f"📚 Document '{filename}' stocké avec embeddings Sentence-BERT")
            
        except Exception as e:
            logging.error(f"Erreur stockage: {e}")

# Instance globale
sentence_bert_service = None

def get_sentence_bert_service():
    """Retourne l'instance du service Sentence-BERT"""
    global sentence_bert_service
    if sentence_bert_service is None:
        sentence_bert_service = SentenceBertDetectionService()
    return sentence_bert_service