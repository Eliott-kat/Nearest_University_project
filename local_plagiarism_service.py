"""
Service de détection de plagiat local utilisant TF-IDF et SentenceTransformer
Traite les documents stockés localement (.docx/.pdf) pour détecter les similarités
"""

import os
import logging
import re
import pickle
import hashlib
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import Counter
import math

from file_utils import extract_text_from_file
from models import Document, db

class LocalPlagiarismService:
    """
    Service de détection de plagiat utilisant des techniques locales :
    - TF-IDF simple implémenté manuellement
    - Similarité cosinus pour la comparaison de textes
    - Base de données locale de documents pour la comparaison
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Base de données des documents
        self.document_database = {}
        self.document_metadata = {}
        
        # Seuils de détection
        self.SIMILARITY_THRESHOLD = 0.3  # 30% similarité minimum pour signaler
        self.HIGH_SIMILARITY_THRESHOLD = 0.7  # 70% similarité élevée
        
        # Chemins de cache
        self.cache_dir = "plagiarism_cache"
        self.database_cache = os.path.join(self.cache_dir, "document_database.pkl")
        self.metadata_cache = os.path.join(self.cache_dir, "document_metadata.pkl")
        
        self._ensure_cache_dir()
        self._load_database()
    
    def _ensure_cache_dir(self):
        """Créer le répertoire de cache s'il n'existe pas"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _load_database(self):
        """Charger la base de données locale des documents"""
        try:
            if os.path.exists(self.database_cache):
                with open(self.database_cache, 'rb') as f:
                    self.document_database = pickle.load(f)
                    
            if os.path.exists(self.metadata_cache):
                with open(self.metadata_cache, 'rb') as f:
                    self.document_metadata = pickle.load(f)
                    
            self.logger.info(f"Base de données chargée : {len(self.document_database)} documents")
            
        except Exception as e:
            self.logger.warning(f"Erreur lors du chargement de la base : {e}")
            self.document_database = {}
            self.document_metadata = {}
    
    def _save_database(self):
        """Sauvegarder la base de données locale"""
        try:
            with open(self.database_cache, 'wb') as f:
                pickle.dump(self.document_database, f)
                
            with open(self.metadata_cache, 'wb') as f:
                pickle.dump(self.document_metadata, f)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la base : {e}")
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Préprocesser le texte en tokens"""
        # Nettoyer et normaliser le texte
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Tokeniser
        words = text.split()
        
        # Filtrer les mots courts et communs
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        words = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return words
    
    def _calculate_tfidf(self, document_words: List[str], all_documents: List[List[str]]) -> Dict[str, float]:
        """Calculer les scores TF-IDF pour un document"""
        # Calculer TF (Term Frequency)
        doc_length = len(document_words)
        tf = Counter(document_words)
        tf_scores = {}
        for word in tf:
            tf_scores[word] = tf[word] / doc_length
        tf = tf_scores
        
        # Calculer IDF (Inverse Document Frequency)
        total_docs = len(all_documents)
        idf = {}
        
        for word in set(document_words):
            docs_containing_word = sum(1 for doc in all_documents if word in doc)
            if docs_containing_word > 0:
                idf[word] = math.log(total_docs / docs_containing_word)
            else:
                idf[word] = 0
        
        # Calculer TF-IDF
        tfidf = {}
        for word in tf:
            tfidf[word] = tf[word] * idf.get(word, 0)
        
        return tfidf
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculer la similarité cosinus entre deux vecteurs TF-IDF"""
        # Obtenir tous les mots uniques
        all_words = set(vec1.keys()) | set(vec2.keys())
        
        if not all_words:
            return 0.0
        
        # Calculer le produit scalaire et les normes
        dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in all_words)
        norm1 = math.sqrt(sum(vec1.get(word, 0) ** 2 for word in all_words))
        norm2 = math.sqrt(sum(vec2.get(word, 0) ** 2 for word in all_words))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _get_document_hash(self, text: str) -> str:
        """Générer un hash unique pour un texte"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extraire les phrases d'un texte"""
        # Découpage simple par phrases
        sentences = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                # Découper par points, mais garder les phrases longues
                parts = line.split('. ')
                for i, part in enumerate(parts):
                    if i < len(parts) - 1:
                        part = part + '.'
                    if len(part.strip()) > 20:  # Phrases d'au moins 20 caractères
                        sentences.append(part.strip())
        return sentences
    
    def add_document_to_database(self, document_path: str, document_id: int = None) -> bool:
        """
        Ajouter un document à la base de données locale pour comparaison future
        """
        try:
            # Extraire le texte du document
            text = extract_text_from_file(document_path, 'text/plain')
            if not text or len(text.strip()) < 100:
                self.logger.warning(f"Document trop court ou vide : {document_path}")
                return False
            
            doc_hash = self._get_document_hash(text)
            
            # Éviter les doublons
            if doc_hash in self.document_database:
                self.logger.info(f"Document déjà dans la base : {document_path}")
                return True
            
            # Préprocesser le texte
            words = self._preprocess_text(text)
            
            # Stocker le document
            self.document_database[doc_hash] = {
                'words': words,
                'original_text': text,
                'sentences': self._extract_sentences(text)
            }
            
            self.document_metadata[doc_hash] = {
                'document_path': document_path,
                'document_id': document_id,
                'added_at': datetime.now().isoformat(),
                'word_count': len(words)
            }
            
            # Sauvegarder la base
            self._save_database()
            
            self.logger.info(f"Document ajouté à la base locale : {document_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout du document {document_path} : {e}")
            return False
    
    def _find_similar_sentences(self, input_text: str, target_sentences: List[str]) -> List[Dict]:
        """Trouver les phrases similaires entre le texte d'entrée et une liste de phrases cibles"""
        matches = []
        input_sentences = self._extract_sentences(input_text)
        
        for i, input_sentence in enumerate(input_sentences):
            input_words = set(self._preprocess_text(input_sentence))
            
            if len(input_words) < 3:  # Ignorer les phrases trop courtes
                continue
                
            for j, target_sentence in enumerate(target_sentences):
                target_words = set(self._preprocess_text(target_sentence))
                
                if len(target_words) < 3:
                    continue
                
                # Calculer la similarité Jaccard (intersection/union)
                intersection = len(input_words & target_words)
                union = len(input_words | target_words)
                
                if union > 0:
                    similarity = intersection / union
                    
                    if similarity >= self.SIMILARITY_THRESHOLD:
                        matches.append({
                            'similarity': similarity,
                            'input_sentence': input_sentence,
                            'target_sentence': target_sentence,
                            'input_index': i,
                            'target_index': j,
                            'common_words': list(input_words & target_words)
                        })
        
        return matches
    
    def analyze_plagiarism(self, text: str) -> Dict:
        """
        Analyser un texte pour détecter le plagiat contre la base locale
        """
        try:
            if not text or len(text.strip()) < 50:
                return {
                    'plagiarism_score': 0,
                    'matches': [],
                    'analysis_method': 'local_simple',
                    'error': 'Texte trop court pour l\'analyse'
                }
            
            if not self.document_database:
                return {
                    'plagiarism_score': 0,
                    'matches': [],
                    'analysis_method': 'local_simple',
                    'total_documents_compared': 0,
                    'message': 'Aucun document dans la base locale pour comparaison'
                }
            
            # Préprocesser le texte d'entrée
            input_words = self._preprocess_text(text)
            all_document_words = [doc_data['words'] for doc_data in self.document_database.values()]
            all_document_words.append(input_words)
            
            # Calculer TF-IDF pour le texte d'entrée
            input_tfidf = self._calculate_tfidf(input_words, all_document_words)
            
            all_matches = []
            max_similarity = 0
            
            # Comparer avec chaque document de la base
            for doc_hash, doc_data in self.document_database.items():
                doc_words = doc_data['words']
                doc_tfidf = self._calculate_tfidf(doc_words, all_document_words)
                
                # Calculer la similarité TF-IDF globale
                tfidf_similarity = self._cosine_similarity(input_tfidf, doc_tfidf)
                
                if tfidf_similarity >= self.SIMILARITY_THRESHOLD:
                    metadata = self.document_metadata.get(doc_hash, {})
                    
                    all_matches.append({
                        'similarity': tfidf_similarity,
                        'method': 'tfidf_local',
                        'document_hash': doc_hash,
                        'document_path': metadata.get('document_path', 'Unknown'),
                        'matched_text': f"Similarité globale: {tfidf_similarity:.2%}",
                        'source_text': f"Document: {os.path.basename(metadata.get('document_path', 'Unknown'))}"
                    })
                    
                    max_similarity = max(max_similarity, tfidf_similarity)
                
                # Analyse des phrases similaires
                sentence_matches = self._find_similar_sentences(text, doc_data['sentences'])
                for match in sentence_matches:
                    if match['similarity'] >= self.SIMILARITY_THRESHOLD:
                        metadata = self.document_metadata.get(doc_hash, {})
                        
                        all_matches.append({
                            'similarity': match['similarity'],
                            'method': 'sentence_similarity',
                            'document_hash': doc_hash,
                            'document_path': metadata.get('document_path', 'Unknown'),
                            'matched_text': match['input_sentence'],
                            'source_text': match['target_sentence'],
                            'common_words': match['common_words']
                        })
                        
                        max_similarity = max(max_similarity, match['similarity'])
            
            # Calculer le score de plagiat final
            plagiarism_score = min(int(max_similarity * 100), 100)
            
            # Trier les correspondances par similarité
            all_matches.sort(key=lambda x: x['similarity'], reverse=True)
            
            return {
                'plagiarism_score': plagiarism_score,
                'matches': all_matches[:10],  # Top 10 des correspondances
                'analysis_method': 'local_simple',
                'total_documents_compared': len(self.document_database),
                'detection_details': {
                    'documents_analyzed': len(self.document_database),
                    'max_similarity': max_similarity,
                    'total_matches': len(all_matches)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de plagiat : {e}")
            return {
                'plagiarism_score': 0,
                'matches': [],
                'analysis_method': 'local_simple',
                'error': str(e)
            }
    

    
    def get_database_stats(self) -> Dict:
        """Obtenir les statistiques de la base de données locale"""
        total_words = sum(meta.get('word_count', 0) for meta in self.document_metadata.values())
        
        return {
            'total_documents': len(self.document_database),
            'total_words': total_words,
            'cache_directory': self.cache_dir,
            'analysis_methods': ['tfidf_local', 'sentence_similarity'],
            'similarity_threshold': self.SIMILARITY_THRESHOLD
        }
    
    def rebuild_database(self):
        """Reconstruire la base de données à partir des documents existants"""
        try:
            self.logger.info("Reconstruction de la base de données de plagiat...")
            
            # Vider les caches
            self.document_database = {}
            self.document_metadata = {}
            
            # Récupérer tous les documents de la base
            documents = Document.query.all()
            
            for doc in documents:
                if doc.file_path and os.path.exists(doc.file_path):
                    self.add_document_to_database(doc.file_path, doc.id)
            
            self.logger.info(f"Base de données reconstruite avec {len(documents)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la reconstruction : {e}")
            return False

# Instance globale du service
local_plagiarism_service = LocalPlagiarismService()