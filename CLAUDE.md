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

Les guides de rôles (accessibles via `openfisca-ai guide cat <name>`) sont des
guides de méthode, pas la preuve qu'un agent runtime existe déjà pour chaque rôle.

Correspondance utile :

- collecte de sources -> `document-collector`
- architecture paramètres -> `parameter-architect`
- implémentation règles -> `rules-engineer`
- génération de tests -> `test-creator`
- revue qualité -> `validators`

## Attendu concret

Si on te demande une implémentation aujourd'hui, le workflow fiable est :

1. charger la config pays
2. lire les docs pertinentes
3. utiliser le code pays existant comme référence
4. modifier le package OpenFisca cible
5. exécuter outils de validation et tests

Présenter ce repo comme un support méthodologique et un toolkit, pas comme un orchestrateur complet déjà abouti.
