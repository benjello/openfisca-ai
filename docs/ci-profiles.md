# CI Profiles

Cette page documente les choix retenus pour normaliser progressivement les CI
GitHub/GitLab autour d'OpenFisca.

## Objectif

L'objectif n'est pas d'imposer une seule CI a tous les repos. Les repos
OpenFisca ont des besoins differents : `openfisca-france` est tres gros,
`openfisca-core` est tres specifique, `openfisca-survey-manager` n'est pas un
package pays, et certains repos sont encore proches d'un outillage legacy.

Le premier niveau stable est donc la detection :

```bash
openfisca-ai ci detect .
```

La sortie YAML decrit le depot et recommande des profils. Elle ne modifie rien.

## Questions Posees

### Combien de profils faut-il ?

Option initiale : beaucoup de profils (`country-uv`, `country-large`,
`extension-uv`, `survey-manager`, `core`, etc.).

Choix retenu : moins de profils, plus lisibles :

- `python-package`
- `openfisca-package`
- `openfisca-large`
- `openfisca-core`
- `openfisca-ai-tools`
- `ai-review`

### Les checks openfisca-ai doivent-ils bloquer les PR ?

Option stricte : `validate-*` et `audit` bloquent la CI.

Option retenue pour la suite : profil informatif par defaut, avec possibilite
future d'un mode strict. Beaucoup de repos existants ont encore des ecarts que
l'audit doit aider a corriger sans bloquer tout le travail.

### GitHub et GitLab doivent-ils etre traites ensemble ?

Option retenue : oui pour la detection, mais la generation devra rester separee :

```bash
openfisca-ai ci plan . --github
openfisca-ai ci plan . --gitlab
```

### Pourquoi ne pas generer les workflows tout de suite ?

Parce que la detection doit etre fiable avant d'ecrire des fichiers CI. Le
workflow cible est :

```text
detect -> plan -> apply
```

- `detect` : observe le depot.
- `plan` : propose les fichiers a creer ou modifier.
- `apply` : ecrit les fichiers apres validation.

## Profils Actuels

### `python-package`

Depot Python classique, pas necessairement OpenFisca pays.

Exemple : `openfisca-survey-manager`.

### `openfisca-package`

Package OpenFisca pays ou extension avec un package `openfisca_*`, des tests et
eventuellement des parametres.

Exemples : `openfisca-tunisia`, `openfisca-france-indirect-taxation`.

### `openfisca-large`

Package OpenFisca avec beaucoup de tests YAML. Ce profil servira plus tard a
proposer une CI avec tests YAML parallelises.

Exemple : `openfisca-france`.

### `openfisca-core`

Depot coeur OpenFisca. Sa CI est specifique et ne doit pas etre reduite a un
profil pays.

### `openfisca-ai-tools`

Profil additionnel pour executer les validations `openfisca-ai` :

- `validate-code`
- `validate-parameters`
- `validate-units`
- `audit`

### `ai-review`

Profil optionnel pour la review automatique de PR. Il depend de secrets LLM et
ne doit pas etre active par defaut sans choix explicite.

## Suite Prevue

1. Ajouter `openfisca-ai ci plan`.
2. Ajouter des templates GitHub/GitLab sous `resources/templates/ci`.
3. Faire de `setup-ci` un wrapper de compatibilite autour de `ci plan/apply`.
4. Ajouter un mode `--strict` pour rendre les validations bloquantes.
