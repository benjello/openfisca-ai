# Instructions Claude - OpenFisca AI

Guide court pour utiliser ce dépôt comme support de travail sur OpenFisca.

## Réalité du dépôt

Ce repo contient aujourd'hui deux couches distinctes :

- **Stable** : outils de validation et gestion de configuration
- **Alpha** : runtime d'agents et pipeline `law_to_code`

Ne pas supposer qu'il sait déjà transformer automatiquement une loi en implémentation OpenFisca prête pour production.

## Ordre de lecture

1. [docs/agents/01-universal/principles.md](docs/agents/01-universal/principles.md)
2. [docs/agents/01-universal/openfisca-basics.md](docs/agents/01-universal/openfisca-basics.md)
3. [docs/agents/01-universal/quality-checklist.md](docs/agents/01-universal/quality-checklist.md)
4. [docs/agents/02-framework/country-config.md](docs/agents/02-framework/country-config.md)
5. Le guide de rôle pertinent dans [docs/agents/02-framework/roles/](docs/agents/02-framework/roles/)
6. La doc pays dans [docs/agents/03-countries/](docs/agents/03-countries/) si nécessaire

## Règles de base

- La loi est la source de vérité.
- Pas de valeurs légales hardcodées.
- Les paramètres doivent être documentés et unités correctement renseignées.
- Les variables doivent être testées.
- Respecter les conventions pays via la config.

## Ce qui marche vraiment

- Chargement de config via `config_loader.py`
- Overrides locaux via `config/user.yaml`
- Outils dans `tools/`
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

Les fichiers de rôles dans `docs/agents/02-framework/roles/` doivent être lus comme des guides de méthode, pas comme la preuve qu'un agent runtime existe déjà pour chaque rôle.

Correspondance utile :

- collecte de sources -> `document-collector.md`
- architecture paramètres -> `parameter-architect.md`
- implémentation règles -> `rules-engineer.md`
- génération de tests -> `test-creator.md`
- revue qualité -> `validators.md`

## Attendu concret

Si on te demande une implémentation aujourd'hui, le workflow fiable est :

1. charger la config pays
2. lire les docs pertinentes
3. utiliser le code pays existant comme référence
4. modifier le package OpenFisca cible
5. exécuter outils de validation et tests

Présenter ce repo comme un support méthodologique et un toolkit, pas comme un orchestrateur complet déjà abouti.
