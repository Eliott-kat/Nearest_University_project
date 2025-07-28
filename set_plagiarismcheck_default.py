#!/usr/bin/env python3
"""
Script pour configurer PlagiarismCheck comme provider par défaut
"""
import os
import sys

# Définir PlagiarismCheck comme provider par défaut
os.environ['PLAGIARISM_API_PROVIDER'] = 'plagiarismcheck'

print("✅ PlagiarismCheck configuré comme provider par défaut")
print(f"Provider actuel: {os.environ.get('PLAGIARISM_API_PROVIDER')}")

# Importer et initialiser l'application après avoir défini la variable
if __name__ == "__main__":
    # Démarrer l'application avec PlagiarismCheck par défaut
    from app import app
    import routes  # noqa: F401
    
    print("🚀 Démarrage de l'application avec PlagiarismCheck...")
    app.run(host="0.0.0.0", port=5000, debug=True)