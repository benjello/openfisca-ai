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

## Resolution Assistee Des Erreurs

Si la premiere passe remonte des erreurs, le plan propose une etape
conditionnelle `resolve-detected-errors` avant toute migration de packaging ou
de CI.

Cette etape ne corrige rien automatiquement. Elle propose de produire un rapport
d'audit, puis de demander a un agent IA de classer les problemes :

- corrections rapides de metadata ;
- valeurs hardcodees ou TODO necessitant une revue metier ;
- tests manquants ;
- faux positifs possibles.

L'objectif est de traiter les erreurs par petits groupes valides par l'humain,
puis de relancer uniquement les checks pertinents.

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

## Politique Des Unites

`openfisca-ai` garde un petit catalogue d'unites generiques (`/1`, `currency`,
`year`, `month`, `kWh`, etc.). Les unites propres a un pays ne doivent pas etre
ajoutees a ce catalogue global.

Quand `init-units` detecte une unite deja utilisee dans un package mais absente
du catalogue generique, il la conserve dans le `units.yaml` genere comme entree
minimale :

```yaml
- name: millimes/kWh
  label: millimes/kWh
```

Cette entree doit ensuite etre validee et enrichie dans le package du pays
concerne. Cela permet de garder les specificites locales sans les transformer en
norme globale.
