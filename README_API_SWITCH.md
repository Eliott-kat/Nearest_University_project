# 🔄 Guide de Migration des APIs

AcadCheck supporte maintenant plusieurs APIs de détection de plagiat. Vous pouvez facilement basculer entre Copyleaks et PlagiarismCheck.

## 🚀 Migration Rapide vers PlagiarismCheck

### Pourquoi basculer ?
- **Plus stable** : L'API PlagiarismCheck a moins de problèmes serveur
- **Plus simple** : Authentication directe par token
- **Plus rapide** : Analyses plus rapides
- **Fallback** : Votre application marche même si une API est en panne

### 📋 Étapes de Migration

#### 1. Obtenez votre Token PlagiarismCheck
1. Visitez https://plagiarismcheck.org/
2. Créez un compte
3. Contactez le support pour obtenir un API token
4. Votre token ressemble à : `vsMKX3179tjK3CqvhE228IDeMV-eBBER`

#### 2. Mettez à jour votre .env

**Option A - Basculement complet :**
```env
# Basculer vers PlagiarismCheck
PLAGIARISM_API_PROVIDER=plagiarismcheck
PLAGIARISMCHECK_API_TOKEN=votre-token-ici

# Gardez Copyleaks en fallback
COPYLEAKS_EMAIL=eliekatende35@gmail.com  
COPYLEAKS_API_KEY=993b468e-6751-478e-9044-06e1a2fb8f75
```

**Option B - Rester sur Copyleaks avec fallback :**
```env
# Rester sur Copyleaks (par défaut)
PLAGIARISM_API_PROVIDER=copyleaks
COPYLEAKS_EMAIL=eliekatende35@gmail.com
COPYLEAKS_API_KEY=993b468e-6751-478e-9044-06e1a2fb8f75

# Ajouter PlagiarismCheck comme backup
PLAGIARISMCHECK_API_TOKEN=votre-token-ici
```

#### 3. Redémarrez l'application
```bash
# Arrêtez l'application (Ctrl+C)
# Puis relancez
python run_local.py
```

### 🔧 Script de Migration Automatique

Exécutez le script d'aide :
```bash
python switch_to_plagiarismcheck.py
```

Ce script vous donne :
- ✅ Instructions détaillées
- ✅ Vérification de votre configuration actuelle  
- ✅ Exemples de configuration .env
- ✅ Liens vers la documentation

### 🔍 Vérification

Après redémarrage, vérifiez les logs :
```
Provider configuré : PlagiarismCheck (utilisation future)
# ou
Provider configuré : Copyleaks
```

### 🎯 Avantages de l'Architecture Multi-API

1. **Redondance** : Si une API tombe, l'autre prend le relais
2. **Flexibilité** : Changez de provider sans modifier le code
3. **Demo Mode** : Fonctionne même sans API configurée
4. **Migration facile** : Une ligne à changer dans .env

### 📊 Comparaison des APIs

| Aspect | Copyleaks | PlagiarismCheck |
|--------|-----------|-----------------|
| Stabilité | ⚠️ Erreurs 500 fréquentes | ✅ Plus stable |
| Setup | 📧 Email + API Key | 🔑 Token unique |
| Features | ✅ Très complet | ✅ Plagiat + IA |
| Documentation | ✅ Complète | ✅ Simple |
| Fallback | ❌ Aucun | ✅ Mode démo |

### 🆘 Support et Dépannage

**Problème : Token PlagiarismCheck invalide**
- Vérifiez le format du token
- Contactez le support PlagiarismCheck

**Problème : Application en mode démo**
- Vérifiez les variables .env
- Regardez les logs pour les erreurs d'authentication

**Revenir à Copyleaks :**
```env
PLAGIARISM_API_PROVIDER=copyleaks
```

### 🔗 Ressources

- [Documentation PlagiarismCheck](https://plagiarismcheck.org/for-developers/)
- [Support PlagiarismCheck](https://plagiarismcheck.org/contact-us/)
- [Documentation Copyleaks](https://api.copyleaks.com/documentation/v3)

---

**💡 Conseil :** Gardez toujours les deux APIs configurées pour une redondance maximale !