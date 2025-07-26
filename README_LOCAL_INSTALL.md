# Installation locale d'AcadCheck

## Prérequis
- Python 3.8+
- pip

## Installation étape par étape

### 1. Téléchargement du projet
Téléchargez tous les fichiers du projet dans un dossier local.

### 2. Installation des dépendances
```bash
pip install flask flask-sqlalchemy flask-login flask-dance
pip install pypdf2 python-docx weasyprint requests
pip install gunicorn psycopg2-binary pyjwt python-dotenv
```

### 3. Configuration avec fichier .env (RECOMMANDÉ)
Créez un fichier `.env` dans le dossier racine du projet :

```env
# Base de données
DATABASE_URL=sqlite:///acadcheck.db

# Sécurité Flask  
SESSION_SECRET=votre-cle-secrete-super-longue-ici

# API Copyleaks - Remplacez par vos vraies données
COPYLEAKS_EMAIL=votre-email@copyleaks.com
COPYLEAKS_API_KEY=votre-cle-api-copyleaks

# Configuration
REPL_ID=acadcheck-local
```

**Important :** Remplacez `votre-email@copyleaks.com` et `votre-cle-api-copyleaks` par vos vraies données Copyleaks.

### 4. Création des dossiers
```bash
mkdir uploads
mkdir uploads/reports
```

### 5. Lancement de l'application
```bash
python main.py
```

L'application sera accessible sur `http://localhost:5000`

## Modes de fonctionnement

### Mode Démonstration
Si vos identifiants Copyleaks ne sont pas valides, l'application fonctionne en mode démonstration avec :
- Analyses automatiques simulées
- Scores de plagiat et IA réalistes
- Phrases surlignées fictives
- Rapports PDF complets

### Mode Production
Avec de vrais identifiants Copyleaks :
- Analyses réelles via l'API Copyleaks
- Scores et détections authentiques
- Pour les webhooks en temps réel, utilisez ngrok :
  ```bash
  ngrok http 5000
  ```

## Sécurité
- Le fichier `.env` contient des données sensibles
- Ajoutez `.env` dans votre `.gitignore`
- Ne partagez jamais vos clés API

## Support
L'application s'adapte automatiquement selon la disponibilité de l'API Copyleaks.