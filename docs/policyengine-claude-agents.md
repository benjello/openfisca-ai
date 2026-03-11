# PolicyEngine Claude – Détail des agents

Résumé détaillé des **21 agents** du plugin [PolicyEngine/policyengine-claude](https://github.com/PolicyEngine/policyengine-claude), pour inspiration dans openfisca-ai.

---

## 1. Country model agents (16)

### Workflow / implémentation

#### **document-collector**
- **Rôle :** Rassembler les **sources officielles** pour l’implémentation de programmes (prestations, crédits d’impôt).
- **Actions :** Recherche et téléchargement de lois, règlements (CFR, codes d’État), manuels, State Plans, calculateurs officiels ; extraction de texte depuis des PDFs (`curl` + `pdftotext`) ; organisation en markdown avec citations.
- **Important :** Signale les règles **non simulables** (limites dans le temps, historique de travail, sanctions progressives) vs partiellement simulables (déductions limitées dans le temps) ; identifie les valeurs dérivées (ex. « 185 % du FPL ») avec preuve juridique.

#### **issue-manager**
- Gestion des **issues et PR** GitHub : création, mise à jour, suivi des tâches liées aux programmes ou aux correctifs.

#### **parameter-architect**
- **Conception des structures de paramètres** : hiérarchie federal/state/local, organisation des fichiers YAML, conventions de nommage et métadonnées (description, label, reference, unit, period).

#### **test-creator**
- **Rédaction de tests** à partir de la documentation et des règles métier : tests unitaires (variables) et d’intégration (scénarios complets), cas limites, calculs manuels documentés en commentaires.

#### **rules-engineer**
- **Implémentation des règles** des programmes (TANF, SNAP, crédits, etc.) en variables et paramètres PolicyEngine.
- **Principes :** La loi est la source de vérité ; **zéro valeur en dur** (tout vient des paramètres) ; utiliser `adds` pour les sommes pures, `add()` pour somme + autre chose ; vérifier Person vs SPMUnit/TaxUnit/Household selon la loi.
- **Réutilise** les patterns des implémentations de référence (DC/IL/TX TANF, etc.) sans copier bêtement (éviter les variables « wrapper » inutiles). Gère « simplified » vs « full » TANF.

#### **pr-pusher**
- **Formatage et envoi des PR** : respect des standards (Black, Prettier, changelog), messages de commit clairs, mise à jour des descriptions de PR.

---

### Validateurs

#### **implementation-validator**
- **Validation globale** des implémentations : qualité, patterns, nommage, séparation federal/state, conformité.
- **Vérifie notamment :** pas de valeurs en dur (sauf 0, 1) ; pas de TODO/placeholders ; paramètres bien organisés et documentés (description en une phrase, label, références avec `#page=XX` pour les PDF) ; usage de `adds` / `add()` ; format `reference` en tuple ; variables avec formule → fichier de test associé ; niveau d’entité correct ; détection de « wrapper variables » inutiles.
- **Produit un rapport structuré** avec correctifs précis que **ci-fixer** peut appliquer (remplacements de code, paramètres à créer, références à corriger).

#### **cross-program-validator**
- Vérification de la **cohérence entre programmes** (même État ou fédéral) : nommage, réutilisation de variables communes, pas de doublons ou incohérences.

#### **performance-optimizer**
- Repérage des **opportunités de vectorisation** et des bonnes pratiques de performance (usage de `where()`, `max_()`, `min_()`, `defined_for`, etc.).

#### **program-reviewer**
- **Revue réglementaire** des implémentations : d’abord **recherche des textes** (manuels, codes, State Plan) pour savoir ce que le programme *doit* faire, puis comparaison au code.
- **Workflow :** (1) WebFetch pour lire les règlements, (2) synthèse structurée (éligibilité, déductions, barèmes, calcul du montant), (3) comparaison PR ↔ règlements, (4) vérification des tests et calculs manuels, (5) rapport (correct / à corriger / couverture de tests), (6) après accord : mise à jour des descriptions d’issue et de PR.
- **Ne modifie pas le code** ; signale les écarts et les manques, puis met à jour la doc issue/PR une fois approuvé.

---

### Qualité et CI

#### **documentation-enricher**
- Enrichissement de la **documentation** : clarification des formules, ajout d’exemples, références, résumés pour les contributeurs.

#### **edge-case-generator**
- Génération de **cas de test** pour les situations limites (revenus nuls, seuils, tailles de ménage, cas géographiques) pour couvrir au mieux les règles.

#### **ci-fixer**
- **Applique les correctifs** proposés par l’implementation-validator (patterns de code, références, paramètres).
- **Lance les tests en local** (ne pas attendre la CI GitHub) et corrige les échecs de tests de manière itérative jusqu’à ce que tout passe.
- S’appuie sur la doc (ex. `sources/working_references.md`, implémentations de référence) pour ne pas « deviner » : comprendre si l’erreur vient du test ou de l’implémentation.

---

### Isolation

#### **isolation-setup**
- Mise en place de **worktrees Git** pour développer de façon isolée (plusieurs branches / programmes en parallèle sans mélanger les fichiers).

#### **isolation-enforcement**
- Vérification que les **tests et l’implémentation** restent bien isolés (pas de fuite entre programmes ou branches).

---

### Autres (country-models)

#### **integration-agent**
- **Workflows de fusion avancés** : coordination entre branches, intégration de plusieurs changements (ex. plusieurs programmes ou États), résolution de conflits de manière cohérente.

---

## 2. Autres agents (5)

#### **branch-comparator**
- **Comparaison de branches** : différences de code, de variables, de paramètres entre deux branches (ex. avant/après une réforme).

#### **legislation-statute-analyzer**
- **Analyse de textes législatifs / réglementaires** : extraction des règles, seuils, formules et conditions à partir de statuts ou de règlements (pour alimenter document-collector ou rules-engineer).

#### **reference-validator**
- **Validation des références** : vérifier que les paramètres (et variables) pointent vers des sources valides (liens, titres, numéros de page pour les PDF) et que les valeurs correspondent aux documents.

#### **api-reviewer**
- **Revue de code** API (Flask) : structure des endpoints, cache, bonnes pratiques REST, cohérence avec policyengine-api.

#### **app-reviewer**
- **Revue de code** de l’application (React) : composants, routing, état, intégration des graphiques, cohérence avec policyengine-app.

---

## Synthèse par type d’usage

| Besoin | Agents principaux |
|--------|---------------------|
| Partir de la loi / doc | document-collector, legislation-statute-analyzer |
| Concevoir paramètres | parameter-architect |
| Implémenter règles | rules-engineer |
| Vérifier qualité / conformité | implementation-validator, program-reviewer, cross-program-validator, reference-validator |
| Tests | test-creator, edge-case-generator |
| Faire passer la CI | ci-fixer |
| Doc et communication | documentation-enricher, issue-manager, pr-pusher |
| Performance | performance-optimizer |
| Isolation / multi-branches | isolation-setup, isolation-enforcement, integration-agent |
| Comparaison / analyse | branch-comparator |
| API / App | api-reviewer, app-reviewer |

---

## Commandes slash (orchestration)

- **`/encode-policy`** : enchaîne plusieurs agents pour **implémenter un programme** de bout en bout (ex. « Idaho LIHEAP »).
- **`/create-pr`** : crée une PR en brouillon, attend que la CI soit verte, puis marque prêt.
- **`/review-pr`** : revue complète (réglementation, références, patterns, tests) et envoi des remarques sur GitHub.
- **`/fix-pr`** : applique les correctifs issus de la revue et pousse les mises à jour.

Ces commandes s’appuient sur les agents ci-dessus (document-collector → parameter-architect → rules-engineer → test-creator → implementation-validator → ci-fixer, etc.).
