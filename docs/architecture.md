# Architecture

`openfisca-ai` regroupe plusieurs niveaux de maturite. Cette page sert de
carte pour eviter de melanger les outils fiables avec les experimentations.

## Stable

La couche stable contient les fonctions qui peuvent etre utilisees comme boite a
outils quotidienne sur des packages OpenFisca.

- Guides methodologiques accessibles avec `openfisca-ai guide ...`.
- Configuration pays et chemins locaux.
- Resolution de targets agent comme `france` ou `tunisie`.
- Validateurs statiques : parametres, unites, code, tests, baseline package.
- Audit consolide et extraction de patterns d'un package existant.

Ces outils doivent rester utilisables sans LLM et avec des sorties testables.

## Beta

La couche beta contient les integrations utiles mais encore a stabiliser.

- Serveur MCP branche sur une API `openfisca serve`.
- Outils MCP qui combinent inspections live et validations locales.

MCP signifie ici : un protocole qui donne a un assistant IA des outils metier,
par exemple chercher une variable, calculer une situation ou auditer un diff.

## Experimental

La couche experimentale contient les brouillons autour de la generation assistee.

- Pipeline `law_to_code`.
- Agents, skills, orchestrateur et abstraction LLM.
- Generation de scaffolds, c'est-a-dire de squelettes de fichiers a relire.
- Application de ces scaffolds dans un package cible.

Ces elements ne doivent pas etre presentes comme une transformation automatique
fiable de la loi vers du code OpenFisca de production.

## Direction Cible

La structure cible est :

```text
openfisca_ai/
  domain/          # concepts metier partages : layout package, unites, rapports
  validators/      # validations fiables
  guides/          # lecture des guides et overlays projet
  config/          # config pays et targets agent
  integrations/    # MCP et autres integrations externes
  experimental/    # agents, LLM, scaffolding, pipelines alpha
```

La migration doit rester progressive : ajouter d'abord les briques communes,
puis faire pointer les anciens modules vers ces briques sans casser la CLI.
