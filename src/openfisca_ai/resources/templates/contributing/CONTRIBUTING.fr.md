# Contribuer à {{project_name}}

Avant tout, merci de votre volonté de contribuer !

## Pré-requis

```bash
git clone <repo-url>
cd {{project_slug}}
uv sync
```

## Vérifications de code automatiques avec pre-commit

Avant chaque commit, des vérifications automatiques sont exécutées via [pre-commit](https://pre-commit.com/).

### Installation

```bash
uv run pre-commit install
```

### Exécuter les vérifications manuellement

```bash
uv run pre-commit run --all-files
```

## Validation avec openfisca-ai

Ce dépôt utilise [openfisca-ai](https://github.com/benjello/openfisca-ai) comme toolkit de validation :

```bash
uv run openfisca-ai validate-parameters .
uv run openfisca-ai validate-units .
uv run openfisca-ai validate-code .
uv run openfisca-ai audit .
```

## Tests

```bash
uv run pytest
```

## Style de code

- Python 3.10+.
- Type hints pour les API publiques.
- Pas de hardcode de valeurs légales — tout dans les YAML de paramètres.

## Format du Changelog

Le [CHANGELOG.md](CHANGELOG.md) est rédigé en français. Sections possibles :

- **Ajouté** : nouvelle fonctionnalité, nouvelle variable, nouveau paramètre.
- **Modifié** : évolution réglementaire, mise à jour, refactoring.
- **Corrigé** : correction d'un bug de calcul ou d'un crash.
- **Supprimé** : retrait d'une variable ou d'un paramètre obsolète.

## Proposer une contribution

1. Vérifiez qu'il n'existe pas déjà une [issue](../../issues) ou une [PR](../../pulls) similaire.
2. Créez une branche à partir de la branche principale.
3. Ajoutez des tests correspondant à vos changements.
4. Validez avec les commandes `openfisca-ai` ci-dessus.
5. Mettez à jour le `CHANGELOG.md`.
6. Soumettez votre PR avec une description claire.
