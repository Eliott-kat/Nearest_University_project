"""
Mode de simulation d'API avec de vrais scores pour démonstration
"""
import os
import time
import random

def simulate_copyleaks_response(text):
    """Simule une vraie réponse Copyleaks avec des scores réalistes"""
    
    # Analyser le contenu pour donner des scores réalistes
    tech_keywords = ['technologie', 'smartphone', 'innovation', 'avancées']
    env_keywords = ['biodiversité', 'écosystème', 'environnement']
    
    has_tech = any(word in text.lower() for word in tech_keywords)
    has_env = any(word in text.lower() for word in env_keywords)
    
    if has_tech:
        # Scores technologiques comme vos tests Copyleaks
        plagiarism_score = random.uniform(30, 40)  # 35.4% comme votre benchmark
        ai_score = random.uniform(95, 100)  # 100% IA comme Copyleaks
    elif has_env:
        # Scores environnementaux très élevés
        plagiarism_score = random.uniform(90, 100)  # 100% comme vos tests
        ai_score = random.uniform(95, 100)  # 100% IA
    else:
        # Scores standards
        plagiarism_score = random.uniform(15, 35)
        ai_score = random.uniform(60, 85)
    
    return {
        "provider_used": "copyleaks_simulation",
        "plagiarism": {
            "percent": round(plagiarism_score, 1),
            "sources_found": random.randint(3, 8),
            "details": [
                {
                    "source": "Academic Database Match",
                    "percent": round(plagiarism_score * 0.6, 1),
                    "confidence": "high"
                },
                {
                    "source": "Internet Source Match", 
                    "percent": round(plagiarism_score * 0.4, 1),
                    "confidence": "medium"
                }
            ],
            "matched_length": len(text) // 3
        },
        "ai_content": {
            "percent": round(ai_score, 1),
            "confidence": "very_high",
            "indicators": ["repetitive_patterns", "academic_language", "ai_typical_phrases"]
        }
    }

def simulate_plagiarismcheck_response(text):
    """Simule une vraie réponse PlagiarismCheck"""
    
    tech_keywords = ['technologie', 'smartphone', 'innovation', 'avancées']
    env_keywords = ['biodiversité', 'écosystème', 'environnement']
    
    has_tech = any(word in text.lower() for word in tech_keywords)
    has_env = any(word in text.lower() for word in env_keywords)
    
    if has_tech:
        plagiarism_score = random.uniform(25, 35)  # Légèrement plus bas que Copyleaks
    elif has_env:
        plagiarism_score = random.uniform(85, 95)  
    else:
        plagiarism_score = random.uniform(10, 30)
    
    return {
        "provider_used": "plagiarismcheck_simulation", 
        "plagiarism": {
            "percent": round(plagiarism_score, 1),
            "sources_found": random.randint(2, 6),
            "details": [
                {
                    "source": "Web Source Match",
                    "percent": round(plagiarism_score, 1),
                    "confidence": "medium"
                }
            ],
            "matched_length": len(text) // 4
        },
        "ai_content": {
            "percent": 0,  # PlagiarismCheck ne fait pas de détection IA
            "confidence": "not_available"
        }
    }

if __name__ == "__main__":
    # Test avec votre texte technologique
    tech_text = """Au cours des dernières décennies, les avancées technologiques ont transformé notre quotidien. Des smartphones aux voitures autonomes, la technologie a modifié notre façon de communiquer, de travailler et de nous déplacer. Cependant, ces innovations soulèvent également des questions éthiques, notamment en matière de vie privée et de sécurité des données. Il est donc essentiel d'aborder ces défis avec prudence."""
    
    print("=== SIMULATION COPYLEAKS ===")
    result1 = simulate_copyleaks_response(tech_text)
    print(f"Plagiat: {result1['plagiarism']['percent']}%")
    print(f"IA: {result1['ai_content']['percent']}%")
    
    print("\n=== SIMULATION PLAGIARISMCHECK ===")
    result2 = simulate_plagiarismcheck_response(tech_text)
    print(f"Plagiat: {result2['plagiarism']['percent']}%")
    print(f"IA: {result2['ai_content']['percent']}%")