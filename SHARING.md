# Partage du Repository - Configuration des Chemins Locaux

Ce document explique comment partager `openfisca-ai` entre utilisateurs avec des chemins locaux différents.

---

## 🎯 Problème

Chaque utilisateur a ses packages OpenFisca à des chemins différents :

```
# Utilisateur A (benjello)
/home/benjello/projets/openfisca-tunisia

# Utilisateur B (alice)
/home/alice/repos/openfisca-tunisia

# Utilisateur C (bob)
/mnt/projects/openfisca/openfisca-tunisia
```

**Solution** : Configuration utilisateur **gitignorée** + template versionné.

---

## ✅ Solution Implémentée

### Fichiers créés

| Fichier | Versionné ? | Usage |
|---------|-------------|-------|
| `config/user.yaml.template` | ✅ Oui | Template à copier |
| `config/user.yaml` | ❌ Non (gitignored) | Configuration personnelle |
| `config/setup.py` | ✅ Oui | Script interactif |
| `.gitignore` | ✅ Oui | Contient `config/user.yaml` |

---

## 🚀 Pour les Nouveaux Utilisateurs

### Méthode 1 : Setup Interactif (Recommandé)

```bash
git clone https://github.com/YOUR_ORG/openfisca-ai
cd openfisca-ai
python config/setup.py
```

**Le script demande** :
1. Chemin de base (ex: `/home/alice/projets`)
2. Pays à configurer (ex: `tunisia, france`)
3. Pays actif par défaut

**Résultat** : Génère `config/user.yaml` automatiquement.

---

### Méthode 2 : Manuel

```bash
git clone https://github.com/YOUR_ORG/openfisca-ai
cd openfisca-ai
cp config/user.yaml.template config/user.yaml
# Éditer config/user.yaml avec vos chemins
```

**Exemple de configuration** :

```yaml
# config/user.yaml
base_path: /home/alice/projets
active_country: tunisia
countries:
  tunisia:
    path: ${base_path}/openfisca-tunisia
  france:
    path: ${base_path}/openfisca-france
```

---

## 📦 Pour Partager le Repo

### 1. Avant de Push

**Vérifiez que `config/user.yaml` n'est PAS dans git** :

```bash
git status
# NE DOIT PAS afficher: config/user.yaml

# Vérifier .gitignore
cat .gitignore | grep user.yaml
# Doit afficher: config/user.yaml
```

---

### 2. Fichiers à Versionner

✅ **À versionner** (commit et push) :
- `config/user.yaml.template` - Template
- `config/setup.py` - Script de configuration
- `config/countries/*.yaml` - Configs pays (sans chemins locaux)
- `.gitignore` - Contient `config/user.yaml`
- `docs/setup/local-configuration.md` - Documentation

❌ **NE JAMAIS versionner** :
- `config/user.yaml` - Chemins locaux personnels
- `.venv/` - Environnement virtuel
- `__pycache__/` - Cache Python

---

## 🔒 Sécurité - Double Vérification

Avant de `git push`, vérifiez :

```bash
# 1. Vérifier .gitignore
grep "config/user.yaml" .gitignore

# 2. Vérifier que user.yaml n'est pas staged
git status | grep user.yaml
# Si affiché → DANGER, faire:
git reset config/user.yaml

# 3. Voir ce qui sera commité
git diff --cached
```

---

## 🌍 Alternatives de Configuration

### Option A : Local (Recommandée)

**Fichier** : `config/user.yaml`

**Avantages** :
- Simple, dans le repo
- Facile à trouver
- Gitignored automatiquement

**Inconvénients** :
- Un fichier par clone du repo
- Risque de commit accidentel (mitigé par .gitignore)

---

### Option B : Global

**Fichier** : `~/.config/openfisca-ai/config.yaml`

**Avantages** :
- Partagé entre tous les clones
- Zéro risque de commit

**Inconvénients** :
- Plus difficile à découvrir
- Configuration "magique" (invisible dans le repo)

**Setup** :
```bash
mkdir -p ~/.config/openfisca-ai
cp config/user.yaml.template ~/.config/openfisca-ai/config.yaml
# Éditer ~/.config/openfisca-ai/config.yaml
```

**Priorité** :
1. `config/user.yaml` (local) — plus haute priorité
2. `~/.config/openfisca-ai/config.yaml` (global)
3. Variables d'environnement

---

### Option C : Variables d'Environnement

**Usage** : CI/CD, overrides temporaires

```bash
export OPENFISCA_AI_BASE_PATH=/tmp/openfisca-test
export OPENFISCA_TUNISIA_PATH=/tmp/openfisca-tunisia

# Utiliser normalement
cd $OPENFISCA_TUNISIA_PATH
uv run python /path/to/openfisca-ai/tools/validate_units.py .
```

---

## 🧪 Tester la Configuration

Après avoir créé `config/user.yaml` :

```bash
# 1. Vérifier le fichier existe
cat config/user.yaml

# 2. Tester avec un outil de validation
cd /path/to/your/openfisca-tunisia
uv run python /path/to/openfisca-ai/tools/validate_units.py .

# 3. Vérifier que git ignore bien le fichier
git status
# config/user.yaml NE DOIT PAS apparaître
```

---

## 📋 Checklist pour Contributeurs

### Avant de Contribuer

- [ ] J'ai créé `config/user.yaml` avec mes chemins locaux
- [ ] `git status` ne montre PAS `config/user.yaml`
- [ ] J'ai testé les outils de validation avec mes chemins

### Avant de Push

- [ ] `git diff --cached` ne contient PAS de chemins locaux personnels
- [ ] `config/user.yaml` est dans `.gitignore`
- [ ] `config/user.yaml.template` est à jour (si j'ai ajouté des champs)

---

## 🐛 Dépannage

### "config/user.yaml apparaît dans git status"

```bash
# 1. Retirer du staging
git reset config/user.yaml

# 2. Vérifier .gitignore
echo "config/user.yaml" >> .gitignore

# 3. Si déjà commité par erreur
git rm --cached config/user.yaml
git commit -m "Remove accidentally committed user config"
```

### "Path not found" lors de l'utilisation d'un outil

```bash
# Vérifier config
cat config/user.yaml

# Vérifier que le chemin existe
ls /path/to/openfisca-tunisia

# Si besoin, re-run setup
python config/setup.py
```

### "J'ai plusieurs clones du repo"

**Solution 1** : Utiliser config global

```bash
mkdir -p ~/.config/openfisca-ai
cp config/user.yaml.template ~/.config/openfisca-ai/config.yaml
# Tous vos clones utiliseront cette config
```

**Solution 2** : Créer `config/user.yaml` dans chaque clone

```bash
cd /path/to/clone1
python config/setup.py

cd /path/to/clone2
python config/setup.py
```

---

## 📚 Documentation Complète

Pour plus de détails, voir :
- [Local Configuration Guide](docs/setup/local-configuration.md)
- [Development Workflow](docs/agents/01-universal/development-workflow.md)
- [Tools README](tools/README.md)

---

## 🎓 Exemple Complet

### Utilisateur : Alice

```bash
# 1. Clone
git clone https://github.com/openfisca/openfisca-ai
cd openfisca-ai

# 2. Configuration
python config/setup.py
# Enter: /home/alice/repos
# Enter: tunisia
# Enter: tunisia (default)

# 3. Vérification
cat config/user.yaml
# base_path: /home/alice/repos
# active_country: tunisia
# countries:
#   tunisia:
#     path: ${base_path}/openfisca-tunisia

# 4. Utilisation
cd /home/alice/repos/openfisca-tunisia
uv run python /home/alice/openfisca-ai/tools/validate_units.py .
# ✅ Fonctionne avec SES chemins

# 5. Contribution
cd /home/alice/openfisca-ai
git add docs/some-improvement.md
git status
# config/user.yaml NOT shown ✅
git commit -m "Add documentation improvement"
git push
# ✅ Pas de chemins personnels partagés
```

---

**Résumé** : Template versionné + config personnelle gitignorée = partage facile ✅
