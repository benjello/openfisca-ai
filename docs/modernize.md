# Modernize

`openfisca-ai modernize` aide a preparer une migration progressive vers un
outillage plus canonique : `pyproject.toml`, `uv`, `ruff`, CI partagee,
validation OpenFisca, etc.

Le principe est volontairement prudent : **proposer, ne pas imposer**.

## Commandes

```bash
openfisca-ai modernize detect .
openfisca-ai modernize plan .
```

Ces commandes n'ecrivent aucun fichier.

## Pourquoi une premiere passe de diagnostic ?

Avant de toucher au packaging ou a la CI, le plan propose de comprendre l'etat
metier du depot :

```bash
uv run openfisca-ai validate-parameters .
uv run openfisca-ai validate-units .
uv run openfisca-ai validate-code .
uv run openfisca-ai validate-tests .
uv run openfisca-ai audit . --markdown --output audit-report.md
uv run openfisca test --country-package <package_name> tests
```

Cette etape evite de confondre deux types de problemes :

- problemes deja presents dans le package ;
- problemes introduits par une migration d'outillage.

## Questions Posees

### Pourquoi `modernize` plutot que `migrate` ?

`migrate` donne l'impression qu'un outil transforme le depot automatiquement.
`modernize` indique mieux qu'il s'agit d'une trajectoire proposee et relue.

### Pourquoi pas d'`apply` maintenant ?

L'application automatique doit arriver plus tard, etape par etape. Les depots
OpenFisca ont des CI et historiques differents. Il faut d'abord obtenir des
plans fiables.

### Pourquoi commencer par les tests OpenFisca ?

Parce que ce sont les garde-fous metier : parametres, unites, formules et tests
doivent etre compris avant de changer le packaging.

## Suite Prevue

1. Ajouter `modernize apply --step <id>` pour des changements tres limites.
2. Ajouter `ci plan` et `ci apply` pour generer les workflows GitHub/GitLab.
3. Ajouter des recettes specifiques pour les cas legacy (`setup.py`, `setup.cfg`,
   `requirements.txt`).
4. Produire des prompts de travail pour agent IA quand une migration demande une
   analyse humaine.
