# Instructions Claude - OpenFisca AI

Guide court pour utiliser ce dépôt comme support de travail sur OpenFisca.

## Réalité du dépôt

Ce repo contient aujourd'hui deux couches distinctes :

- **Stable** : outils de validation et gestion de configuration
- **Alpha** : runtime d'agents et pipeline `law_to_code`

Ne pas supposer qu'il sait déjà transformer automatiquement une loi en implémentation OpenFisca prête pour production.

## Ordre de lecture

Les guides sont packagés dans `src/openfisca_ai/resources/agents/` et accessibles
via la commande `openfisca-ai guide` (depuis n'importe quel projet ayant
openfisca-ai en dépendance).

```bash
uv run openfisca-ai guide list                # liste les guides
uv run openfisca-ai guide cat principles      # affiche un guide
uv run openfisca-ai guide show test-creator   # chemin absolu
```

Lecture recommandée :

1. `principles` — règles fondamentales
2. `openfisca-basics` — variables, entités, paramètres
3. `quality-checklist` — vérifications avant commit
4. `country-config` — chargement de la config pays
5. Le guide de rôle pertinent : `document-collector`, `parameter-architect`,
   `rules-engineer`, `test-creator`, `validators`
6. Doc pays : `03-countries/<pays>/specifics`

## Règles de base

- La loi est la source de vérité.
- Pas de valeurs légales hardcodées.
- Les paramètres doivent être documentés et unités correctement renseignées.
- Les variables doivent être testées.
- Respecter les conventions pays via la config.

## Ce qui marche vraiment

- Chargement de config via `config_loader.py`
- Overrides locaux via `config/user.yaml`
- Outils de validation autonomes dans `tools/` exposés via la CLI
- Guides packagés accessibles via `openfisca-ai guide`
- **Serveur MCP** branché sur l'API web OpenFisca (`openfisca-ai mcp`) — voir
  section dédiée plus bas
- CLI minimal : `uv run openfisca-ai run <task.json>`

## Ce qui n'est pas implémenté

- Pas de vrai système multi-agents autonome
- `ExtractorAgent` et `CoderAgent` sont encore des placeholders
- Les commandes `/encode-policy`, `/review-pr`, `/fix-pr` n'existent pas dans le repo

## Configuration

Exemple d'usage :

```python
from openfisca_ai.config_loader import load_country_config, get_reference_code_path

config = load_country_config("tunisia")
reference_code_path = get_reference_code_path("tunisia")
```

Exemple de `config/user.yaml` :

```yaml
countries:
  tunisia:
    existing_code:
      path: /path/to/openfisca-tunisia
    legislative_sources:
      root: /path/to/tunisia-laws
```

## Commandes recommandées

Dans ce repo :

```bash
uv sync --dev
uv run python config/test_config.py
uv run pytest
uv run openfisca-ai run tasks/example_task.json
```

Dans un package OpenFisca pays :

```bash
cd /path/to/openfisca-country
uv run python /path/to/openfisca-ai/tools/validate_units.py .
uv run python /path/to/openfisca-ai/tools/validate_parameters.py .
uv run python /path/to/openfisca-ai/tools/check_tooling.py .
```

## Utilisation comme agent

Les guides de rôles sont des **patterns de méthode**, pas des identités
exclusives. Une seule tâche "implémenter une variable" enchaîne typiquement
plusieurs patterns en séquence :

1. `document-collector` — trouver les sources légales
2. `parameter-architect` — poser les YAML de paramètres
3. `rules-engineer` — écrire la formule
4. `test-creator` — produire les tests YAML
5. `validators` — auditer le résultat

Tu n'as pas à "choisir un rôle" : applique les patterns dans l'ordre utile pour
la tâche. Sauter des étapes est OK quand elles sont déjà faites.

Lecture : `uv run openfisca-ai guide cat <name>`.

## Serveur MCP

Le serveur MCP expose une instance live d'OpenFisca comme outils pour les
agents (exploration, calcul, trace).

**Source de vérité unique** : `uv run openfisca-ai guide cat mcp`. Ce guide
décrit la liste exacte des outils, le coût d'amorçage, et la stratégie
"static vs MCP par tâche" — la règle simpliste "static d'abord" ne s'applique
qu'à l'audit ; pour implémenter ou générer un test, MCP est plus efficace.

Démarrage rapide :

```bash
uv run openfisca-ai mcp --serve \
  --serve-command "uv run openfisca serve --country-package openfisca_<country>"
```

Dans un projet avec un `.mcp.json`, Claude Code détecte le serveur
automatiquement.

## Attendu concret

Si on te demande une implémentation aujourd'hui, le workflow fiable est :

1. charger la config pays
2. lire les docs pertinentes
3. utiliser le code pays existant comme référence
4. modifier le package OpenFisca cible
5. exécuter outils de validation et tests

Présenter ce repo comme un support méthodologique et un toolkit, pas comme un orchestrateur complet déjà abouti.
