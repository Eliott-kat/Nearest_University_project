# Guide d'Installation Locale - AcadCheck

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.8 ou plus récent**
- **pip** (gestionnaire de packages Python)
- **Git** (optionnel, pour cloner le projet)

## 🚀 Installation Rapide

### 1. Télécharger le projet

```bash
# Option 1: Cloner avec Git
git clone https://github.com/votre-username/acadcheck.git
cd acadcheck

# Option 2: Télécharger et extraire le ZIP
# Puis naviguer dans le dossier extrait
```

### 2. Créer un environnement virtuel

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate

# Sur macOS/Linux:
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements_local.txt
```

Si le fichier `requirements_local.txt` n'existe pas, installez manuellement :

```bash
pip install flask flask-sqlalchemy flask-login flask-wtf
pip install werkzeug requests python-dotenv
pip install pypdf2 python-docx weasyprint
pip install scikit-learn numpy psycopg2-binary
pip install gunicorn email-validator pyjwt
```

### 4. Configuration

Créez un fichier `.env` dans le dossier racine :

```bash
# Fichier .env
DATABASE_URL=sqlite:///acadcheck.db
FLASK_SECRET_KEY=votre-cle-secrete-ici
FLASK_ENV=development
FLASK_DEBUG=True

# APIs optionnelles (pour détection avancée)
COPYLEAKS_API_KEY=votre-cle-copyleaks
COPYLEAKS_EMAIL=votre-email-copyleaks
PLAGIARISMCHECK_API_TOKEN=votre-token-plagiarismcheck
```

### 5. Initialiser la base de données

```bash
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Base de données initialisée avec succès!')
"
```

### 6. Lancer l'application

```bash
# Option 1: Script automatique (RECOMMANDÉ)
python run_local.py

# Option 2: Mode développement manuel
python main.py

# Option 3: Mode production avec Gunicorn
gunicorn --bind 127.0.0.1:5000 main:app

# Option 4: Flask run
export FLASK_APP=main.py
flask run --host=0.0.0.0 --port=5000
```

**Le script `run_local.py` est recommandé car il :**
- Configure automatiquement l'environnement
- Utilise SQLite au lieu de PostgreSQL
- Vérifie les dépendances
- Initialise la base de données
- Lance l'application avec les bons paramètres

## 🌐 Accès à l'application

Une fois lancée, ouvrez votre navigateur et accédez à :

**http://localhost:5000** ou **http://127.0.0.1:5000**

## 📁 Structure du projet

```
acadcheck/
├── app.py              # Configuration Flask principale
├── main.py             # Point d'entrée de l'application
├── models.py           # Modèles de base de données
├── routes.py           # Routes et logique métier
├── auth_simple.py      # Système d'authentification
├── file_utils.py       # Gestion des fichiers
├── unified_detection_service.py  # Services de détection
├── report_generator.py # Génération de rapports
├── static/             # CSS, JS, images
├── templates/          # Templates HTML
├── uploads/            # Dossier des fichiers téléchargés
├── instance/           # Base de données SQLite
└── .env               # Variables d'environnement
```

## 🔧 Dépannage

### Problème avec WeasyPrint

Si l'installation de WeasyPrint échoue :

```bash
# Sur Ubuntu/Debian:
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# Sur macOS:
brew install pango

# Puis réinstaller:
pip install weasyprint
```

### Problème avec psycopg2

Si vous n'utilisez pas PostgreSQL, modifiez le `DATABASE_URL` dans `.env` :

```bash
DATABASE_URL=sqlite:///acadcheck.db
```

### Port déjà utilisé

Si le port 5000 est occupé, changez le port :

```bash
python main.py --port 8000
# ou modifiez directement dans main.py
```

## 🔑 APIs Optionnelles

L'application fonctionne sans APIs externes, mais pour une détection avancée :

1. **Copyleaks** : Inscrivez-vous sur https://copyleaks.com
2. **PlagiarismCheck** : Obtenez un token sur https://plagiarismcheck.org

Ajoutez les clés dans le fichier `.env`.

## 🛡️ Sécurité en Local

- Changez `FLASK_SECRET_KEY` par une valeur aléatoire
- Ne partagez jamais votre fichier `.env`
- Utilisez HTTPS en production
- Sauvegardez régulièrement votre base de données

## 📞 Support

En cas de problème :

1. Vérifiez que Python 3.8+ est installé
2. Assurez-vous que l'environnement virtuel est activé
3. Consultez les logs d'erreur dans le terminal
4. Vérifiez que tous les packages sont installés

L'application devrait maintenant fonctionner parfaitement en local !