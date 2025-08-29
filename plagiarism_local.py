import os
from rapidfuzz import fuzz
from simhash import Simhash

# Dossier où stocker les documents de référence (corpus local)
REFERENCE_DIR = os.path.join(os.path.dirname(__file__), 'reference_corpus')
os.makedirs(REFERENCE_DIR, exist_ok=True)

def get_reference_texts():
    """Charge tous les textes de référence du dossier corpus."""
    texts = []
    for fname in os.listdir(REFERENCE_DIR):
        path = os.path.join(REFERENCE_DIR, fname)
        if os.path.isfile(path):
            with open(path, encoding='utf-8', errors='ignore') as f:
                texts.append((fname, f.read()))
    return texts

def plagiarism_score_rapidfuzz(submitted_text: str, reference_texts=None):
    """Calcule le score de plagiat maximal avec RapidFuzz (similaire à Turnitin/Copyleaks)."""
    if reference_texts is None:
        reference_texts = get_reference_texts()
    max_score = 0
    best_source = None
    for fname, ref in reference_texts:
        score = fuzz.token_set_ratio(submitted_text, ref)
        if score > max_score:
            max_score = score
            best_source = fname
    return {'score': max_score, 'source': best_source}

def plagiarism_score_simhash(submitted_text: str, reference_texts=None):
    """Calcule la similarité Simhash (rapide, robuste pour gros corpus)."""
    if reference_texts is None:
        reference_texts = get_reference_texts()
    submitted_hash = Simhash(submitted_text)
    min_distance = 64
    best_source = None
    for fname, ref in reference_texts:
        ref_hash = Simhash(ref)
        distance = submitted_hash.distance(ref_hash)
        if distance < min_distance:
            min_distance = distance
            best_source = fname
    # Convertir la distance en score (0 = identique, 64 = très différent)
    score = 100 - int((min_distance / 64) * 100)
    return {'score': score, 'source': best_source}

if __name__ == "__main__":
    # Exemple d'utilisation
    test = "Paste your document text here."
    print("RapidFuzz:", plagiarism_score_rapidfuzz(test))
    print("Simhash:", plagiarism_score_simhash(test))
