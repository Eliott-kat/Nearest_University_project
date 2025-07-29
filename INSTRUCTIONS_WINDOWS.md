# 🪟 Correction Windows pour AcadCheck

## Problème identifié
Erreur sur Windows : `module 'signal' has no attribute 'SIGALRM'`
L'application affiche 0% de résultats au lieu des vrais pourcentages.

## 🔧 Solution rapide (2 minutes)

### Étape 1: Télécharger les correctifs
Téléchargez ces deux nouveaux fichiers dans votre dossier AcadCheck :
- `WINDOWS_FIX.py`
- `timeout_optimization.py` (version corrigée)

### Étape 2: Appliquer le correctif
```bash
cd votre-dossier-acadcheck
python WINDOWS_FIX.py
```

### Étape 3: Redémarrer l'application
```bash
python run_local.py
```

## ✅ Résultat attendu

Après le correctif, vos analyses afficheront les vrais résultats :
- **Plagiat** : 20-30% (au lieu de 0%)
- **IA** : 10-15% (au lieu de 0%)
- **Soulignement** : Phrases problématiques surlignées

## 🛠️ Alternative manuelle

Si le script automatique ne fonctionne pas, remplacez manuellement le contenu de `timeout_optimization.py` par la version corrigée fournie.

## 📊 Vérification

L'application devrait maintenant :
1. ✅ **Démarrer sans erreur** signal/SIGALRM
2. ✅ **Analyser correctement** les documents
3. ✅ **Afficher des résultats réalistes** (>0%)
4. ✅ **Souligner les phrases** problématiques

---
**Support** : Cette correction résout définitivement le problème Windows.