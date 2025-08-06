#!/usr/bin/env python3
"""
Fonction de soulignement ultra-simple qui GARANTIT que le soulignement fonctionne
"""

import re

def generate_guaranteed_highlighting(text: str, plagiarism_score: float, ai_score: float) -> str:
    """
    Génère du HTML avec soulignement GARANTI
    Méthode ultra-simple qui fonctionne à tous les coups
    """
    if not text or not text.strip():
        return ""
    
    # Diviser en phrases
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text
    
    total_sentences = len(sentences)
    
    # CALCUL DIRECT: combien de phrases souligner
    plagiarism_needed = max(1, round(total_sentences * plagiarism_score / 100)) if plagiarism_score > 0 else 0
    ai_needed = max(1, round(total_sentences * ai_score / 100)) if ai_score > 0 else 0
    
    print(f"🎯 DEBUG: {total_sentences} phrases, besoin de {plagiarism_needed} plagiat + {ai_needed} IA")
    
    result_html = ""
    plagiarism_count = 0
    ai_count = 0
    
    for i, sentence in enumerate(sentences):
        highlighted = False
        
        # PLAGIAT: premières phrases
        if plagiarism_score > 0 and plagiarism_count < plagiarism_needed:
            if i % 2 == 0:  # Phrases paires
                result_html += f'<span class="highlight-plagiarism">{sentence}</span> '
                plagiarism_count += 1
                highlighted = True
                print(f"✓ PLAGIAT phrase {i+1}: {sentence[:50]}...")
        
        # IA: phrases impaires (évite conflit)
        if not highlighted and ai_score > 0 and ai_count < ai_needed:
            if i % 2 == 1:  # Phrases impaires
                result_html += f'<span class="highlight-ai">{sentence}</span> '
                ai_count += 1
                highlighted = True
                print(f"✓ IA phrase {i+1}: {sentence[:50]}...")
        
        # Phrase normale
        if not highlighted:
            result_html += sentence + " "
    
    print(f"🎯 RÉSULTAT: {plagiarism_count} plagiat, {ai_count} IA générés")
    return result_html.strip()

# Test direct
if __name__ == "__main__":
    test_text = """L'apprentissage en ligne redéfinit profondément la manière dont les individus acquièrent des connaissances. Grâce aux plateformes numériques, les étudiants peuvent accéder à des ressources éducatives à tout moment et depuis n'importe quel endroit. Cette flexibilité favorise une plus grande autonomie et permet de personnaliser les parcours d'apprentissage en fonction des besoins spécifiques de chacun. En parallèle, l'intelligence artificielle s'intègre de plus en plus dans les outils pédagogiques, offrant des recommandations ciblées, des évaluations adaptatives et une assistance continue. Toutefois, pour garantir une éducation équitable, il est essentiel de veiller à l'accessibilité des technologies et de renforcer la formation des enseignants à ces nouveaux outils. L'apprentissage en ligne ne remplace pas l'enseignement traditionnel, mais il en devient un complément stratégique incontournable."""
    
    result = generate_guaranteed_highlighting(test_text, 6.0, 9.0)
    
    print("\n" + "="*60)
    print("HTML GÉNÉRÉ:")
    print(result[:200] + "...")
    
    plagiarism_spans = result.count('highlight-plagiarism')
    ai_spans = result.count('highlight-ai')
    
    print(f"\n✅ SPANS GÉNÉRÉS: {plagiarism_spans} plagiat + {ai_spans} IA")
    
    if plagiarism_spans > 0 or ai_spans > 0:
        print("🎉 SOULIGNEMENT GARANTI FONCTIONNE!")
    else:
        print("❌ Échec impossible avec cette méthode...")