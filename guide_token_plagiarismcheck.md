# 🔑 Guide Complet : Obtenir un Token PlagiarismCheck

## 📋 ÉTAPES POUR OBTENIR VOTRE TOKEN

### **Option 1 : Contact Direct Support (RECOMMANDÉ)**

1. **Créez un compte sur PlagiarismCheck.org**
   - Visitez : https://plagiarismcheck.org/
   - Cliquez sur "Sign Up" pour créer un compte

2. **Contactez le Support pour l'API**
   - **Email :** support@plagiarismcheck.org
   - **Téléphone :** +1 844 319 5147 (24/7)
   - **Objet :** "Request API Token for Integration"

3. **Votre message en français :**
```
Objet : Demande de token API pour plateforme éducative

Bonjour,

Je développe AcadCheck, une plateforme d'intégrité académique pour 
les établissements d'enseignement, et souhaiterais intégrer votre API 
de détection de plagiat et d'IA.

Pourriez-vous me fournir un token API pour commencer l'intégration ?

Détails du projet :
- Application : AcadCheck (analyse d'intégrité académique)
- Secteur : Éducation - universités et écoles
- Usage : Vérification de documents étudiants (mémoires, dissertations)
- Volume estimé : [précisez vos besoins]
- Objectif : Améliorer l'intégrité académique avec détection IA + plagiat

L'intégration permettra aux enseignants de vérifier automatiquement 
l'authenticité des travaux étudiants.

Merci pour votre aide,
[Votre nom]
[Votre établissement/organisation]
```

### **Option 2 : Dashboard Account (Si Disponible)**

Si vous avez déjà un compte premium :
1. Connectez-vous à votre compte
2. Allez dans **Profile → Integrations**
3. Cliquez sur **"Get API Token"**
4. Copiez votre token

## 🔍 FORMATS DE TOKEN

Votre token ressemblera à :
```
vsMKX3179tjK3CqvhE228IDeMV-eBBER
cUwhcQU88K2cYn47aPCg-snWoSNNJwyW
```

## ⚙️ CONFIGURATION DANS ACADCHECK

Une fois que vous avez le token :

1. **Ajoutez-le dans votre fichier .env :**
```env
# Votre token PlagiarismCheck
PLAGIARISMCHECK_API_TOKEN=vsMKX3179tjK3CqvhE228IDeMV-eBBER

# Gardez aussi Copyleaks comme fallback
COPYLEAKS_EMAIL=eliekatende35@gmail.com
COPYLEAKS_API_KEY=993b468e-6751-478e-9044-06e1a2fb8f75

# Provider principal (garder copyleaks, PlagiarismCheck sera en fallback)
PLAGIARISM_API_PROVIDER=copyleaks
```

2. **Redémarrez l'application :**
```bash
# Arrêtez avec Ctrl+C puis relancez
python run_local.py
```

## 🎯 AVANTAGES DE PLAGIARISMCHECK

✅ **Plus stable** que Copyleaks (moins d'erreurs 500)  
✅ **API simple** avec token unique  
✅ **Détection IA incluse** (TraceGPT AI Detector)  
✅ **Support 24/7** disponible  
✅ **Documentation claire** avec exemples  

## 🧪 TEST DE VOTRE TOKEN

Testez votre token avec cette commande :
```bash
curl "https://plagiarismcheck.org/api/v1/text" \
  --request POST \
  --header "X-API-TOKEN: VOTRE-TOKEN-ICI" \
  --data "language=en" \
  --data "text=Test de plagiat avec un texte de plus de 80 caractères pour vérifier que l'API fonctionne correctement avec notre application AcadCheck."
```

## 💰 TARIFICATION

- **Pas de prix public** pour l'API
- **Tarification personnalisée** selon usage
- **Plans organization :** $69 - $599 (usage général)
- **API Enterprise :** Devis sur demande

## ⚡ RÉSULTAT ATTENDU

Avec PlagiarismCheck configuré :

**Avant :** Copyleaks échoue → Mode démonstration  
**Après :** Copyleaks échoue → PlagiarismCheck testé → Résultats réels ou mode démo seulement si les deux échouent

Vous verrez dans les logs :
```
Service principal échoué, tentative avec PlagiarismCheck
Basculement réussi vers PlagiarismCheck
```

## 📞 CONTACTS SUPPORT

**Email :** support@plagiarismcheck.org  
**Téléphone :** +1 844 319 5147  
**Adresse :** London, UK (Dixcart House, Surrey)  

## 🎮 SCRIPTS DE TEST INCLUS

Une fois configuré, testez avec :
```bash
python test_fallback.py
```

---

**💡 Conseil :** Mentionnez que vous utilisez le système pour l'éducation - cela peut accélérer l'obtention du token !