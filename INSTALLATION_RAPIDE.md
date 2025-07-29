# Installation Rapide AcadCheck (Version ZIP)

## Problème : L'algorithme retourne 0%

Cela arrive quand les dépendances Python ne sont pas installées correctement sur votre machine locale.

## Solution en 3 étapes :

### 1. Installer Python 3.11+ 
Téléchargez depuis : https://www.python.org/downloads/
⚠️ **Important** : Cochez "Add to PATH" pendant l'installation

### 2. Installer les dépendances
Ouvrez un terminal/invite de commande dans le dossier AcadCheck et tapez :

```bash
pip install flask flask-sqlalchemy flask-login
pip install python-docx pypdf2 weasyprint 
pip install requests python-dotenv werkzeug
pip install scikit-learn numpy nltk
```

Ou utilisez cette commande unique :
```bash
pip install flask flask-sqlalchemy flask-login python-docx pypdf2 weasyprint requests python-dotenv werkzeug scikit-learn numpy nltk
```

### 3. Lancer l'application
```bash
python run_local.py
```

## Vérification rapide

Pour tester si tout fonctionne, créez ce fichier test.py :

```python
# test.py
import sys
sys.path.append('.')

from sentence_bert_detection import SentenceBertDetection

# Test simple
detector = SentenceBertDetection()
result = detector.detect_plagiarism("La biodiversité est essentielle pour notre planète.")
print(f"Test résultat : {result}")
```

Puis tapez : `python test.py`

## Si ça ne marche toujours pas :

### Option A : Environnement virtuel (recommandé)
```bash
python -m venv venv
# Windows :
venv\Scripts\activate
# Mac/Linux :
source venv/bin/activate

# Puis installer les dépendances
pip install flask flask-sqlalchemy flask-login python-docx pypdf2 weasyprint requests python-dotenv werkzeug scikit-learn numpy nltk
```

### Option B : Problème WeasyPrint (PDF)
Si WeasyPrint pose problème, désactivez temporairement la génération PDF en commentant cette ligne dans `report_generator.py` :
```python
# from weasyprint import HTML
```

## Pourquoi 0% ?

L'algorithme retourne 0% quand :
1. ❌ **scikit-learn** manque (détection IA)
2. ❌ **numpy** manque (calculs matriciels)
3. ❌ **nltk** manque (traitement du langage)

Avec toutes les dépendances installées, vous devriez obtenir des résultats comme :
- ✅ 24% plagiat détecté
- ✅ 10% contenu IA détecté

## Test final

Après installation, uploadez un document et vous devriez voir dans les logs :
```
INFO:root:🎯 Détection complète: 24.15% plagiat + 10.2% IA
INFO:root:Succès avec turnitin_local: 24.1% plagiat détecté
```