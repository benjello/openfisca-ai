# Documentation pour agents IA - OpenFisca AI

Architecture à 3 niveaux pour guider les agents IA (Claude, Cursor, Gemini, etc.) dans le codage de législation avec OpenFisca.

## Structure

```
docs/agents/
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
Les points d'entrée principaux résument ou référencent ces 3 niveaux :
- [CLAUDE.md](../../CLAUDE.md) pour Claude
- [.cursorrules](../../.cursorrules) pour Cursor
- [AI_AGENTS.md](../../AI_AGENTS.md) pour autres agents

### Pour développeurs
1. Lire [01-universal/principles.md](01-universal/principles.md) en premier
2. Poser la structure cible avec [01-universal/country-package-baseline.md](01-universal/country-package-baseline.md)
3. Consulter [02-framework/roles/](02-framework/roles/) selon la tâche
4. Vérifier [03-countries/<pays>/specifics.md](03-countries/) si aménagements

## Ajout d'un nouveau pays

1. Créer `config/countries/<pays>.yaml` (voir [_schema.yaml](../../config/countries/_schema.yaml))
2. Optionnel : créer `docs/agents/03-countries/<pays>/specifics.md` si déviations
3. Le runtime Python peut charger la config via `config_loader.py`

## Inspiration

Le projet est inspiré par les workflows agents de PolicyEngine, mais le dépôt actuel reste volontairement plus simple et centré sur OpenFisca.
