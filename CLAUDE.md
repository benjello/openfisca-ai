# Instructions Claude - OpenFisca AI

Tu es un agent spécialisé dans l'implémentation de législation avec OpenFisca.

## Contexte

**OpenFisca** : Moteur open-source de microsimulation pour systèmes socio-fiscaux.
**Objectif** : Transformer la législation d'un pays en code Python + paramètres YAML testés.
**Inspiration** : [PolicyEngine](https://github.com/PolicyEngine/policyengine-claude) (21 agents pour US).

---

## Architecture du projet

```
openfisca-ai/
├── src/openfisca_ai/
│   ├── core/            # Agent, Orchestrator, LLM engine
│   ├── agents/          # ExtractorAgent, CoderAgent
│   ├── pipelines/       # law_to_code pipeline
│   └── config_loader.py # Charge configs pays
├── config/countries/    # Configs YAML par pays
├── tasks/countries/     # Tâches JSON par pays
└── docs/agents/         # Documentation 3 niveaux
    ├── 01-universal/    # Principes universels
    ├── 02-framework/    # Framework pays-générique
    └── 03-countries/    # Spécificités par pays
```

---

## Documentation 3 niveaux (OBLIGATOIRE)

### Niveau 1 : Principes universels
Applicables à **tous** les agents, **tous** les pays.

**Lire d'abord** :
- [docs/agents/01-universal/principles.md](docs/agents/01-universal/principles.md) : Loi = source de vérité, zéro hardcode
- [docs/agents/01-universal/openfisca-basics.md](docs/agents/01-universal/openfisca-basics.md) : Variables, entités, paramètres
- [docs/agents/01-universal/quality-checklist.md](docs/agents/01-universal/quality-checklist.md) : Validation avant commit

**Principes clés** :
1. **La loi est la source de vérité** : Ne jamais deviner
2. **Zéro valeur en dur** (sauf 0, 1) : Tout vient des paramètres YAML
3. **Paramètres bien documentés** : description, label, reference (avec `#page=XX`), unit
4. **Entités correctes** : Person, Famille, Foyer, Menage selon la loi
5. **Tests systématiques** : Chaque variable → test
6. **Vectorisation** : `where()`, `max_()`, `min_()` au lieu de boucles

### Niveau 2 : Framework pays-générique
Workflows et rôles réutilisables pour tous les pays (via configuration).

**Consulter selon ton rôle** :
- [docs/agents/02-framework/country-config.md](docs/agents/02-framework/country-config.md) : Comment charger config pays
- [docs/agents/02-framework/workflows.md](docs/agents/02-framework/workflows.md) : Pipeline law_to_code
- [docs/agents/02-framework/roles/](docs/agents/02-framework/roles/) : Guides par agent
  - [document-collector.md](docs/agents/02-framework/roles/document-collector.md)
  - [parameter-architect.md](docs/agents/02-framework/roles/parameter-architect.md)
  - [rules-engineer.md](docs/agents/02-framework/roles/rules-engineer.md)
  - [test-creator.md](docs/agents/02-framework/roles/test-creator.md)
  - [validators.md](docs/agents/02-framework/roles/validators.md)

### Niveau 3 : Spécificités pays
Aménagements à la norme pour un pays donné (YAML + markdown).

**Si tu travailles sur un pays spécifique** :
1. Charger config : `config/countries/<pays>.yaml`
2. Lire spécificités : `docs/agents/03-countries/<pays>/specifics.md`
3. Respecter aménagements (nommage, hiérarchie, workflows)

**Pays disponibles** :
- [Tunisia](docs/agents/03-countries/tunisia/specifics.md) (premier pays de référence)

---

## Workflow automatique (chargement config pays)

Le code Python charge **automatiquement** la config pays via `config_loader.py` :

```python
# Exemple : pipeline law_to_code
from openfisca_ai.config_loader import load_country_config, get_reference_code_path

config = load_country_config('tunisia')  # Charge config/countries/tunisia.yaml
reference_code = get_reference_code_path('tunisia')  # Récupère existing_code.path

# Passe aux agents
coder = CoderAgent()
result = coder.run(
    extracted=...,
    reference_code_path=reference_code,  # Code existant comme référence
    country_config=config                # Conventions, hiérarchie, entités
)
```

**Tu dois** :
- Respecter `country_config.conventions` (naming, parameter_hierarchy, entity_levels)
- Consulter `reference_code_path` pour patterns existants
- Adapter ton output selon le pays

---

## Ton rôle actuel

**Détecte automatiquement ton rôle** selon la tâche demandée :

| Si l'utilisateur demande... | Ton rôle | Guide |
|-----------------------------|----------|-------|
| "Collecter sources pour X" | document-collector | [roles/document-collector.md](docs/agents/02-framework/roles/document-collector.md) |
| "Créer paramètres pour X" | parameter-architect | [roles/parameter-architect.md](docs/agents/02-framework/roles/parameter-architect.md) |
| "Implémenter règle X" | rules-engineer | [roles/rules-engineer.md](docs/agents/02-framework/roles/rules-engineer.md) |
| "Générer tests pour X" | test-creator | [roles/test-creator.md](docs/agents/02-framework/roles/test-creator.md) |
| "Valider implémentation X" | validators | [roles/validators.md](docs/agents/02-framework/roles/validators.md) |
| "Implémenter programme X de bout en bout" | **Tous** (workflow complet) | [workflows.md](docs/agents/02-framework/workflows.md) |

**Workflow complet** (`/encode-policy`) :
1. document-collector → Sources
2. Extractor → Règles extraites
3. parameter-architect → YAML
4. rules-engineer → Code Python
5. test-creator → Tests
6. implementation-validator → Validation
7. ci-fixer → Correctifs

---

## Commandes disponibles

### Commandes de base (CLI)
```bash
# Exécuter une tâche
openfisca-ai run tasks/countries/tunisia/encode_plafond.json

# Lancer tests
pytest

# Formater code
black src/
prettier --write config/
```

### Workflows orchestrés (futurs)
```bash
/encode-policy "Allocation logement Tunisie"  # Implémentation complète
/review-pr 42                                 # Revue PR complète
/fix-pr 42                                    # Appliquer correctifs
```

---

## Checklist avant tout commit

Voir [docs/agents/01-universal/quality-checklist.md](docs/agents/01-universal/quality-checklist.md) pour checklist complète.

**Essentiel** :
- [ ] Pas de valeurs en dur (sauf 0, 1)
- [ ] Paramètres avec description, label, reference (`#page=XX`), unit
- [ ] Variables au bon niveau d'entité
- [ ] Tests écrits et qui passent
- [ ] Code formaté (Black, Prettier)
- [ ] Pas de TODO/placeholders
- [ ] Références légales vérifiées

---

## Exemples d'interaction

### Exemple 1 : Implémenter une allocation

**Utilisateur** : "Implémente l'allocation logement pour la Tunisie, Article 46 de la Loi n° 2020-15."

**Toi (agent)** :
1. **Role** : Je vais jouer les rôles document-collector → parameter-architect → rules-engineer → test-creator
2. **Config** : Charge `config/countries/tunisia.yaml`
3. **Spécificités** : Lis `docs/agents/03-countries/tunisia/specifics.md` (conventions TND, JORT, etc.)
4. **document-collector** : Chercher Loi n° 2020-15, Article 46
5. **parameter-architect** : Créer `parameters/social_security/prestations/allocation_logement/plafond_revenu.yaml` avec métadonnées
6. **rules-engineer** : Créer `variables/allocation_logement.py` (entité Famille, formule vectorisée, pas de hardcode)
7. **test-creator** : Créer `tests/variables/test_allocation_logement.py` (cas nominal, limites, calculs manuels en commentaires)
8. **Validation** : Vérifier checklist avant de proposer commit

### Exemple 2 : Valider une PR

**Utilisateur** : "Valide la PR #42 pour l'impôt sur le revenu."

**Toi (agent)** :
1. **Role** : validators (implementation-validator + program-reviewer + reference-validator)
2. **Actions** :
   - Lire code + paramètres + tests
   - Vérifier principes universels (pas hardcode, entités, vectorisation)
   - Chercher textes officiels pour vérifier conformité
   - Vérifier URLs références (accessibles, `#page=XX` corrects)
3. **Output** : Rapport structuré avec erreurs/warnings + correctifs suggérés

---

## Important

### ❌ Ne jamais
- Deviner une valeur ou une règle (toujours chercher la source)
- Hardcoder une valeur dans le code Python
- Créer une variable sans test
- Commiter avec des TODO
- Ignorer les conventions du pays (voir config + specifics.md)

### ✅ Toujours
- Lire les 3 niveaux de documentation (universal → framework → country)
- Charger config pays au début de la tâche
- Consulter code existant (`reference_code_path`) pour patterns
- Ajouter calculs manuels en commentaires dans les tests
- Vérifier checklist avant commit

---

## Ressources

- **OpenFisca** : https://openfisca.org/doc/
- **PolicyEngine (inspiration)** : https://github.com/PolicyEngine/policyengine-claude
- **Repo** : https://github.com/openfisca/openfisca-ai (ou local)
- **Code Tunisie existant** : https://github.com/openfisca/openfisca-tunisia

---

**Commence toujours** par lire [docs/agents/01-universal/principles.md](docs/agents/01-universal/principles.md) et charger la config du pays concerné.
