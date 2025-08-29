import numpy as np
import torch
import re
from typing import List, Tuple, Dict, Any
import os
from collections import defaultdict
import time

# Cache pour les modèles et données de référence
_MODEL_CACHE = {}
_REFERENCE_CACHE = {}
_PLAGIARISM_CACHE = {}

# --------- Initialisation optimisée des modèles ---------
def get_model():
    """Charge le modèle une seule fois avec mise en cache"""
    if 'model' not in _MODEL_CACHE:
        from transformers import GPT2LMHeadModel, GPT2TokenizerFast
        
        print("Chargement du modèle GPT-2...")
        _MODEL_CACHE['tokenizer'] = GPT2TokenizerFast.from_pretrained('distilgpt2')
        _MODEL_CACHE['model'] = GPT2LMHeadModel.from_pretrained('distilgpt2')
        _MODEL_CACHE['model'].eval()
        # Configuration pour une meilleure performance
        if torch.cuda.is_available():
            _MODEL_CACHE['model'] = _MODEL_CACHE['model'].to('cuda')
    
    return _MODEL_CACHE['model'], _MODEL_CACHE['tokenizer']

# --------- Plagiat Exact (TF-IDF + Cosine) optimisé ---------
def preprocess_text(text: str, min_length: int = 10) -> List[str]:
    """Sépare le texte en phrases en conservant la ponctuation."""
    if not text or not text.strip():
        return []
    
    # Version plus efficace de la séparation des phrases
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > min_length]

def get_reference_data(ignore_filename=None):
    """Charge et cache les données de référence une seule fois, possibilité d'ignorer un fichier"""
    cache_key = 'reference_data' if ignore_filename is None else f'reference_data_{ignore_filename}'
    if cache_key in _REFERENCE_CACHE:
        return _REFERENCE_CACHE[cache_key]
    
    REFERENCE_DIR = os.path.join(os.path.dirname(__file__), 'reference_corpus')
    if not os.path.exists(REFERENCE_DIR):
        _REFERENCE_CACHE[cache_key] = ([], None, None)
        return _REFERENCE_CACHE[cache_key]
        
    texts = []
    ref_sentences = []
    
    for fname in os.listdir(REFERENCE_DIR):
        if ignore_filename and fname == ignore_filename:
            continue
        path = os.path.join(REFERENCE_DIR, fname)
        if os.path.isfile(path):
            try:
                with open(path, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    texts.append((fname, content))
                    ref_sentences.extend(preprocess_text(content, 20))  # Seuil plus élevé pour les références
            except Exception as e:
                print(f"Error reading file {fname}: {str(e)}")
    
    # Vectoriser une seule fois
    from sklearn.feature_extraction.text import TfidfVectorizer
    if ref_sentences:
        vectorizer = TfidfVectorizer().fit(ref_sentences)
        ref_vecs = vectorizer.transform(ref_sentences)
    else:
        vectorizer = None
        ref_vecs = None
    
    _REFERENCE_CACHE[cache_key] = (texts, vectorizer, ref_vecs)
    return texts, vectorizer, ref_vecs

def tfidf_cosine_plagiarism_optimized(submitted_text: str, ignore_filename=None) -> float:
    """Version optimisée de la détection de plagiat avec calibration pour Turnitin"""
    submitted_sentences = preprocess_text(submitted_text, 20)
    if not submitted_sentences:
        return 0.0

    _, vectorizer, ref_vecs = get_reference_data(ignore_filename=ignore_filename)

    # Heuristique "suspect" si corpus absent ou vide
    def suspicious_heuristic(sentences):
        if not sentences:
            return 0.0
        long_phrases = [s for s in sentences if len(s) > 120]
        repeated = len(sentences) != len(set(sentences))
        unique_ratio = len(set(sentences)) / len(sentences) if sentences else 1
        score = 0.0
        if long_phrases:
            score += 5
        if repeated:
            score += 3
        if unique_ratio < 0.7:
            score += 2
        return min(10, score)

    if ref_vecs is None or vectorizer is None:
        return suspicious_heuristic(submitted_sentences)

    submitted_vecs = vectorizer.transform(submitted_sentences)
    from sklearn.metrics.pairwise import cosine_similarity
    sim_matrix = cosine_similarity(submitted_vecs, ref_vecs)

    if sim_matrix.size == 0:
        return suspicious_heuristic(submitted_sentences)

    threshold = 0.7
    weighted_scores = []
    for i in range(sim_matrix.shape[0]):
        max_sim = np.max(sim_matrix[i])
        if max_sim > threshold:
            sentence_length = len(submitted_sentences[i])
            weight = min(1.0, sentence_length / 100)
            weighted_scores.append(max_sim * weight)

    if not weighted_scores:
        # Si aucune phrase n'est détectée comme plagiée, appliquer l'heuristique
        return suspicious_heuristic(submitted_sentences)

    raw_score = np.mean(weighted_scores) * 100
    calibrated_score = 15 * np.log(1 + raw_score / 15)
    # Si le score calibré est très faible (< 10), on prend le max avec l'heuristique
    return min(100, max(calibrated_score, suspicious_heuristic(submitted_sentences)))

# --------- Algorithme IA optimisé (inchangé) ---------
def perplexity_optimized(text, model, tokenizer):
    """Version optimisée du calcul de perplexité"""
    if not text or not text.strip():
        return 1000.0  # Valeur par défaut élevée pour texte vide
    
    encodings = tokenizer(text, return_tensors='pt')
    
    # Utiliser GPU si disponible
    if torch.cuda.is_available():
        encodings = {k: v.to('cuda') for k, v in encodings.items()}
    
    max_length = model.config.n_positions
    stride = 256  # Réduction du stride pour plus d'efficacité
    seq_len = encodings.input_ids.size(1)
    
    nlls = []
    prev_end_loc = 0
    
    for begin_loc in range(0, seq_len, stride):
        end_loc = min(begin_loc + max_length, seq_len)
        trg_len = end_loc - prev_end_loc
        input_ids = encodings.input_ids[:, begin_loc:end_loc]
        target_ids = input_ids.clone()
        
        with torch.no_grad():
            outputs = model(input_ids, labels=target_ids)
            neg_log_likelihood = outputs.loss * trg_len
        
        nlls.append(neg_log_likelihood)
        prev_end_loc = end_loc
        if end_loc == seq_len:
            break
    
    if not nlls:
        return 1000.0
        
    ppl = torch.exp(torch.stack(nlls).sum() / seq_len)
    return float(ppl)

def burstiness_optimized(text, model, tokenizer, max_sentences=10):
    """Version optimisée du calcul de burstiness avec échantillonnage"""
    sentences = [s for s in split_sentences(text) if len(s) > 10]
    
    if len(sentences) < 3:
        return 0.0
    
    # Échantillonnage pour éviter de traiter trop de phrases
    if len(sentences) > max_sentences:
        indices = np.random.choice(len(sentences), max_sentences, replace=False)
        sentences = [sentences[i] for i in indices]
    
    ppls = []
    for s in sentences:
        ppl = perplexity_optimized(s, model, tokenizer)
        ppls.append(ppl)
        # Petite pause pour éviter la surcharge
        time.sleep(0.01)
    
    ppls = np.array(ppls)
    return float(np.std(ppls) / np.mean(ppls)) if np.mean(ppls) > 0 else 0.0

def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)

def ai_detection_score_optimized(text: str) -> Dict[str, Any]:
    """Version optimisée de la détection IA avec calibration pour Turnitin/CopyLeaks"""
    if not text or len(text) < 100:  # Texte trop court
        return {
            "score": 0.0,
            "perplexity": 0.0,
            "burstiness": 0.0,
            "details": {
                "norm_ppl": 0.0,
                "norm_burstiness": 0.0
            }
        }
    
    model, tokenizer = get_model()
    
    # Calcul en parallèle si possible
    ppl = perplexity_optimized(text, model, tokenizer)
    burst = burstiness_optimized(text, model, tokenizer)
    
    # Nouvelle calibration pour correspondre à Turnitin/CopyLeaks
    # Ajustement des formules de normalisation
    if ppl < 20:  # Très basse perplexité (forte indication IA)
        norm_ppl = min(100, max(0, (20 - ppl) * 10))
    elif ppl > 100:  # Très haute perplexité (forte indication humaine)
        norm_ppl = 0
    else:  # Zone intermédiaire
        norm_ppl = max(0, min(100, 100 - (ppl - 20) * 1.25))
    
    # Ajustement de la burstiness
    if burst < 0.05:  # Très basse burstiness (forte indication IA)
        norm_burst = min(100, max(0, (0.05 - burst) * 2000))
    elif burst > 0.5:  # Très haute burstiness (forte indication humaine)
        norm_burst = 0
    else:  # Zone intermédiaire
        norm_burst = max(0, min(100, 100 * (1 - burst / 0.5)))
    
    # Pondération ajustée pour correspondre aux détecteurs commerciaux
    score = 0.5 * norm_ppl + 0.5 * norm_burst
    
    # Ajustement final pour réduire les faux positifs
    # Les textes académiques bien rédigés ont souvent des scores bas
    if ppl > 50 and burst > 0.1:  # Caractéristiques de texte humain
        score = score * 0.3  # Réduction significative du score
    
    return {
        "score": round(score, 1),
        "perplexity": round(ppl, 1),
        "burstiness": round(burst, 3),
        "details": {
            "norm_ppl": round(norm_ppl, 1),
            "norm_burstiness": round(norm_burst, 1)
        }
    }

# --------- Fusion des scores de plagiat ---------
def fusion_plagiarism_score(submitted_text: str, ignore_filename=None) -> Tuple[float, float, float]:
    """Combine les scores de plagiat exact et sémantique."""
    exact = tfidf_cosine_plagiarism_optimized(submitted_text, ignore_filename=ignore_filename)
    semantic = 0.0  # Désactivé pour l'instant
    combined = exact
    return round(combined, 1), exact, semantic

# --------- Interface principale optimisée ---------
def analyze_text(text: str, ignore_filename=None) -> Dict[str, Any]:
    """Analyse un texte pour le plagiat et la génération IA."""
    start_time = time.time()
    
    # Détection de plagiat
    plagiarism_score, exact_score, semantic_score = fusion_plagiarism_score(text, ignore_filename=ignore_filename)
    
    # Détection de contenu généré par IA
    ai_result = ai_detection_score_optimized(text)
    
    end_time = time.time()
    
    return {
        "plagiarism": {
            "score": plagiarism_score,
            "exact_match": exact_score,
            "semantic_similarity": semantic_score
        },
        "ai_generated": ai_result,
        "text_stats": {
            "length": len(text),
            "sentences": len(preprocess_text(text, 10))
        },
        "processing_time": round(end_time - start_time, 2)
    }

if __name__ == "__main__":
    # Test avec un exemple de texte
    test_text = """
    Artificial intelligence is transforming various industries by providing innovative solutions 
    to complex problems. Machine learning algorithms can analyze large datasets to identify patterns 
    and make predictions with remarkable accuracy. This technology is being applied in healthcare, 
    finance, and many other sectors to improve efficiency and decision-making processes.
    """
    
    results = analyze_text(test_text)
    
    print("=== RÉSULTATS D'ANALYSE ===")
    print(f"Temps de traitement: {results['processing_time']}s")
    print(f"Score de plagiat: {results['plagiarism']['score']}%")
    print(f"  - Correspondance exacte: {results['plagiarism']['exact_match']}%")
    print(f"  - Similarité sémantique: {results['plagiarism']['semantic_similarity']}%")
    print(f"Score de contenu IA: {results['ai_generated']['score']}%")
    print(f"  - Perplexité: {results['ai_generated']['perplexity']}")
    print(f"  - Burstiness: {results['ai_generated']['burstiness']}")
    print(f"  - Perplexité normalisée: {results['ai_generated']['details']['norm_ppl']}%")