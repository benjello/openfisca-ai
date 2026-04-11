# Documentation pour agents IA - OpenFisca AI

Architecture à 3 niveaux pour guider les agents IA (Claude, Cursor, Gemini, etc.) dans le codage de législation avec OpenFisca.

## Structure

```
src/openfisca_ai/resources/agents/
├── 01-universal/         # Niveau 1 : Principes universels (tous agents, tous pays)
│   ├── principles.md     # Loi = source de vérité, zéro hardcode
│   ├── openfisca-basics.md  # Entités, variables, paramètres OpenFisca
│   ├── country-package-baseline.md # Structure commune des packages pays
│   └── quality-checklist.md # Checklist validation avant commit
│
├── 02-framework/         # Niveau 2 : Framework pays-générique
│   ├── country-config.md # Comment configurer un pays
│   ├── workflows.md      # Pipelines law_to_code
│   └── roles/            # Guides par agent
│       ├── document-collector.md
│       ├── parameter-architect.md
│       ├── rules-engineer.md
│       ├── test-creator.md
│       └── validators.md
│
└── 03-countries/         # Niveau 3 : Spécificités par pays
    ├── _template.md      # Template pour nouveau pays
    └── tunisia/
        └── specifics.md  # Aménagements à la norme (YAML + markdown)
```

## Architecture à 3 niveaux

### Niveau 1 : Principes universels
Applicables à **tous les agents**, **tous les pays**, **toutes les tâches**.
- La loi est la source de vérité
- Zéro valeur en dur (sauf 0, 1)
- Paramètres bien documentés (description, label, reference)
- Tests systématiques
- Vectorisation et performance
- Baseline commune des packages pays (`pyproject.toml`, `entities.py`, `units.yaml`, `tests/`, CI)

→ Voir [01-universal/](01-universal/)

### Niveau 2 : Framework pays-générique
**Réutilisable** pour tous les pays via **configuration**.
- Comment un pays se configure (YAML)
- Workflows et pipelines standards
- Rôles d'agents avec prompts réutilisables

→ Voir [02-framework/](02-framework/)

### Niveau 3 : Spécificités par pays
**Aménagements** à la norme pour un pays donné.
- Configuration technique (YAML)
- Explications des déviations (markdown)
- Workflows spécifiques optionnels

→ Voir [03-countries/](03-countries/)

## Utilisation

### Pour agents IA (Claude, Cursor, etc.)
Les guides sont accessibles depuis n'importe quel projet qui dépend
d'openfisca-ai via :

```bash
uv run openfisca-ai guide list
uv run openfisca-ai guide cat <name>
uv run openfisca-ai guide show <name>
```

Les points d'entrée principaux du repo openfisca-ai eux-mêmes :
- `CLAUDE.md` pour Claude
- `.cursorrules` pour Cursor
- `AI_AGENTS.md` pour autres agents

### Pour développeurs
1. Lire `principles` en premier (`openfisca-ai guide cat principles`)
2. Poser la structure cible avec `country-package-baseline`
3. Consulter le rôle pertinent : `document-collector`, `parameter-architect`,
   `rules-engineer`, `test-creator`, `validators`
4. Vérifier `03-countries/<pays>/specifics` si aménagements

### Outils CLI complémentaires aux guides

- Validation statique : `openfisca-ai audit .`, `openfisca-ai validate-*`
- Serveur MCP (live, sémantique) : `openfisca-ai mcp --serve`
- Génération de test à partir d'une trace : `openfisca-ai generate-test-from-trace trace.json`

Les guides `rules-engineer`, `test-creator` et `validators` détaillent comment
combiner ces outils par rôle.

### Overlays projet

Un projet consommateur peut surcharger un guide en plaçant un fichier au même
chemin relatif sous `docs/openfisca-ai/agents/`. Exemple pour étendre le guide
test-creator :

```
mon-projet/
└── docs/openfisca-ai/agents/02-framework/roles/test-creator.md
```

`openfisca-ai guide cat test-creator` retournera alors le guide générique suivi
de la section « Spécificités projet » contenant l'overlay.

## Ajout d'un nouveau pays

1. Créer `config/countries/<pays>.yaml` (voir `config/countries/_schema.yaml`)
2. Optionnel : créer `src/openfisca_ai/resources/agents/03-countries/<pays>/specifics.md` si déviations
3. Le runtime Python peut charger la config via `config_loader.py`

## Inspiration

Le projet est inspiré par les workflows agents de PolicyEngine, mais le dépôt actuel reste volontairement plus simple et centré sur OpenFisca.
