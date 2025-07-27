# 🚀 Guide GPTZero : Troisième Option de Fallback

## 📋 POURQUOI AJOUTER GPTZERO ?

GPTZero est maintenant intégré comme **troisième option de fallback** dans votre système AcadCheck, offrant :

### ✅ **Avantages uniques :**
- **Double service :** Détection IA (99%+ précision) + Plagiat dans une seule API
- **Haute précision :** 96.5% pour contenu mixte humain/IA
- **Faibles faux positifs :** <1% de taux d'erreur
- **Focus académique :** Spécialement conçu pour l'éducation
- **Highlighting granulaire :** Détection jusqu'au niveau phrase
- **API simple :** Un seul token, réponse immédiate

## 🔄 NOUVEL ORDRE DE FALLBACK

Votre système teste maintenant automatiquement dans cet ordre :

```
1. Copyleaks (principal) 
   ↓ (si échec)
2. PlagiarismCheck 
   ↓ (si échec)  
3. GPTZero (nouveau!)
   ↓ (si échec)
4. Mode démonstration (dernier recours)
```

## 💰 TARIFICATION GPTZERO

| Plan | Prix/mois | Mots/mois | API Incluse |
|------|-----------|-----------|-------------|
| **Premium** | $16-24 | 300,000 | ✅ |
| **Professional** | $25-30 | 500,000 | ✅ |

## 🔑 OBTENIR VOTRE CLÉ API

### **Étape 1 : Inscription**
1. Visitez : https://gptzero.me/pricing
2. Choisissez le plan **Premium** (minimum pour API)
3. Créez votre compte

### **Étape 2 : Récupérer la clé API**
1. Connectez-vous à : https://app.gptzero.me/app/api
2. Cliquez sur **"View API Key"**
3. Copiez votre clé (format : `gpt_xxxxxxxxxxxxx`)

### **Étape 3 : Configuration**
Ajoutez dans votre fichier `.env` :
```env
# GPTZero API (troisième fallback)
GPTZERO_API_KEY=gpt_votre_cle_ici
```

## 🧪 TEST RAPIDE

Testez votre configuration :
```bash
python -c "
from gptzero_service_class import GPTZeroService
service = GPTZeroService()
print('GPTZero configuré:', service.is_configured())
print('Test auth:', service.authenticate())
"
```

## 📊 RÉSULTAT ATTENDU

Avec GPTZero ajouté, vos analyses seront **beaucoup plus fiables** :

**Avant :** Copyleaks échoue → PlagiarismCheck échoue → Mode démo (résultats factices)

**Maintenant :** Copyleaks échoue → PlagiarismCheck échoue → **GPTZero analyse réelle** → Mode démo seulement si tout échoue

## 🎯 AVANTAGES POUR VOTRE APPLICATION

### **Fiabilité accrue :**
- **3 APIs réelles** avant mode démo
- **Couverture maximale** des pannes
- **Continuité de service** assurée

### **Qualité d'analyse :**
- **GPTZero excelle** dans la détection IA
- **Complément parfait** à Copyleaks/PlagiarismCheck
- **Focus éducation** adapté à AcadCheck

### **Expérience utilisateur :**
- **Moins d'analyses factices**
- **Résultats plus fiables**
- **Service quasi-continu**

## 📝 LOGS QUE VOUS VERREZ

Avec GPTZero configuré :
```
INFO: Service principal: Copyleaks, fallback: PlagiarismCheck → GPTZero
WARNING: Échec authentification Copyleaks
WARNING: Échec authentification PlagiarismCheck  
INFO: Basculement vers GPTZero réussi
INFO: Soumission réussie avec GPTZero après basculement
```

## 💡 CONSEIL D'OPTIMISATION

**Budget limité ?** Configurez seulement GPTZero pour commencer :
- **$16/mois** pour 300k mots
- **Double service** (IA + plagiat)
- **Plus fiable** que Copyleaks actuellement
- **Moins cher** que Copyleaks Premium

Votre application AcadCheck devient **professionnelle** avec cette triple protection anti-panne !

## 🔗 LIENS UTILES

- **Site GPTZero :** https://gptzero.me
- **Dashboard API :** https://app.gptzero.me/app/api
- **Documentation :** https://gptzero.me/developers
- **Support :** Via dashboard GPTZero

---

**Résultat :** Votre plateforme AcadCheck sera désormais **ultra-fiable** avec trois APIs de qualité avant de tomber en mode démonstration !