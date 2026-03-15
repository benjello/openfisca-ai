# Spécificités pays : Tunisie

Aménagements à la norme OpenFisca AI pour la Tunisie.

## Vue d'ensemble

Premier pays implémenté dans openfisca-ai. Ce fichier sera enrichi au fur et à mesure que des spécificités émergeront.

**Code existant** : [openfisca/openfisca-tunisia](https://github.com/openfisca/openfisca-tunisia)

---

## Configuration

Voir `config/countries/tunisia.yaml` pour la configuration technique.

```yaml
id: tunisia
label: Tunisia
legislative_sources:
  root: [à configurer dans config/user.yaml]
existing_code:
  path: [à configurer dans config/user.yaml]
conventions:
  parameter_hierarchy:
    - gov
    - social_security
    - taxation
  entity_levels:
    - Person
    - Famille
    - Foyer
    - Menage
  naming: snake_case
```

---

## Aménagements identifiés

**Basés sur analyse de** : [openfisca-tunisia](https://github.com/openfisca/openfisca-tunisia) (439 paramètres YAML, 40 fichiers variables)

### 0. Métadonnées multilingues (Français + Arabe) 🔮 FUTUR

**Exigence future** : Tous les champs de métadonnées (descriptions, labels) DEVRONT être fournis en **français (défaut)** et **arabe** quand OpenFisca Core supportera cette fonctionnalité.

#### Langues
- **Défaut** : Français (`fr`)
- **Supportées** : Français (`fr`) + Arabe (`ar`)

#### Champs concernés
- `description` (dans les paramètres)
- `label` (dans les paramètres et units.yaml)
- `short_label` (dans units.yaml)

#### Format units.yaml (actuel → cible)

**Actuel** (français uniquement) :
```yaml
- name: currency
  label:
    one: Dinar
    other: Dinars
  short_label: DT
```

**Cible** (français + arabe) :
```yaml
- name: currency
  label:
    fr:
      one: Dinar
      other: Dinars
    ar:
      one: دينار
      other: دنانير
  short_label:
    fr: DT
    ar: د.ت

- name: smig
  label:
    fr:
      one: Smig
      other: Smigs
    ar:
      one: الأجر الأدنى المضمون
      other: الأجر الأدنى المضمون
```

#### Format paramètres (français + arabe)

```yaml
description:
  fr: Pension minimale garanti de la CNRPS
  ar: الحد الأدنى للمعاش المضمون من الصندوق الوطني للتقاعد
label:
  fr: Pension minimale CNRPS
  ar: معاش أدنى CNRPS
reference:
  - "Loi n° XX, Article YY"
  - "القانون عدد XX، الفصل YY"
unit: smig
values:
  1974-01-01: 0.66666
```

#### Termes courants (Français → Arabe)

| Français | Arabe | Contexte |
|----------|-------|----------|
| Dinar | دينار | Monnaie |
| millime | مليم | 1/1000 dinar |
| Smig | الأجر الأدنى المضمون | Salaire minimum |
| pension | معاش | Retraite |
| retraite | تقاعد | Retraite |
| salaire | أجر | Salaire |
| impôt | ضريبة | Impôt |
| cotisation | اشتراك | Cotisation sociale |
| allocation | إعانة | Allocation |
| famille | عائلة | Famille |
| enfant | طفل | Enfant |
| CNRPS | الصندوق الوطني للتقاعد والحيطة الاجتماعية | Caisse retraite publique |
| CNSS | الصندوق الوطني للضمان الاجتماعي | Caisse sécurité sociale |

#### Statut
- Français : ✅ Implémenté (métadonnées actuelles)
- Arabe : ❌ **Pas encore supporté par OpenFisca Core**

**IMPORTANT** : OpenFisca Core ne supporte **pas encore** la structure multilingue (clés `fr`/`ar` imbriquées). Cette exigence est documentée comme **objectif futur** pour la Tunisie, en attente d'évolution d'OpenFisca Core.

**Solution temporaire** : Garder métadonnées en français uniquement (statu quo). Documenter traductions arabes séparément en commentaires ou fichier annexe.

#### Contexte légal
La Tunisie est un **pays officiellement bilingue** (français/arabe) :
- **Français** : Langue de la plupart de la législation moderne (post-indépendance)
- **Arabe** : Langue officielle nationale, utilisée dans les lois récentes et l'administration publique

**Accessibilité** : Les deux langues garantissent que :
- Les professionnels du droit peuvent référencer les textes officiels dans les deux langues
- Les citoyens peuvent comprendre leurs droits/obligations en arabe
- La coopération internationale est facilitée par le français

---

### 1. Hiérarchie de paramètres (spécifique Tunisie)

**Hiérarchie effective** dans openfisca-tunisia (différente de la norme suggérée) :

```
parameters/
├── energie/                    # Énergie (électricité, gaz)
├── fiscalite_indirecte/       # TVA, accises
├── impot_revenu/              # Impôt sur le revenu
│   ├── bic/                   # Bénéfices industriels et commerciaux
│   ├── bnc/                   # Bénéfices non commerciaux
│   ├── deductions/
│   ├── foncier/
│   ├── tspr/                  # Taxe spécifique
│   └── ...
├── marche_travail/            # SMIG, etc.
├── prelevements_sociaux/      # Cotisations sociales
│   ├── atmp/                  # Accidents du travail
│   ├── cotisations_sociales/
│   └── contribution_sociale_solidarite/
├── prestations/
│   ├── contributives/         # Prestations familiales
│   └── non_contributives/     # AMG, PNAFN
└── retraite/
    ├── cnrps/                 # Fonction publique ⚠️
    ├── rsa/                   # Salariés agricoles ⚠️
    └── rsna/                  # Salariés non agricoles ⚠️
```

**⚠️ Différence majeure** : `retraite/` au même niveau que `prestations/`, pas dedans.

**Raison** : Trois régimes de retraite distincts en Tunisie (voir ci-dessous).

---

### 2. Trois régimes de retraite (SPÉCIFIQUE TUNISIE)

**Important** : La Tunisie a 3 régimes de retraite distincts avec paramètres séparés.

| Régime | Nom complet | Population |
|--------|-------------|------------|
| **CNRPS** | Caisse Nationale de Retraite et de Prévoyance Sociale | Fonctionnaires |
| **RSA** | Régime Salariés Agricoles | Salariés agricoles |
| **RSNA** | Régime Salariés Non Agricoles | Salariés non-agricoles (privé) |

**Impact** :
- Paramètres dupliqués par régime (ex: `age_legal`, `pension_minimale`, `bareme_annuite`)
- Variables spécifiques par régime
- Tests séparés

**Exemple** : `parameters/retraite/cnrps/bareme_annuite.yaml` avec historique depuis 1959.

---

### 3. SMIG comme unité de référence

**SMIG** (Salaire Minimum Interprofessionnel Garanti) = équivalent tunisien du SMIC.

#### SMIG 40h vs SMIG 48h
```python
# Exemple: prestations_familiales.py ligne 158
smig48 = parameters(period.start).marche_travail.smig_48h_mensuel
```

**Deux types** :
- SMIG 40h/semaine (secteur général)
- SMIG 48h/semaine (certains secteurs)

#### SMIG comme unit dans paramètres
**Observation** : Certains paramètres utilisent `unit: smig` au lieu de `TND`.

```yaml
# parameters/retraite/cnrps/pension_minimale/minimum_garanti.yaml
description: Pension minimale garanti de la CNRPS
values:
  1974-01-01:
    value: 0.66666
metadata:
  unit: smig  # ⚠️ Paramètre en multiple du SMIG
```

**Raison** : Valeurs indexées sur le SMIG (évoluent automatiquement avec le SMIG).

**Pattern à utiliser** : Si paramètre dérivé du SMIG → `unit: smig` acceptable.

---

### 4. Calculs trimestriels

**Observation** : Beaucoup de prestations calculées par trimestre, puis annualisées.

**Exemple** : `prestations_familiales.py` ligne 87-108
```python
# Le montant trimestriel est calculé...
bm = ... / 4  # base trimestrielle
af_base = (...)  # Calcul trimestriel
return 4 * af_base  # annualisé
```

**Pattern** :
1. Diviser revenus annuels par 4
2. Calculer prestation trimestrielle
3. Multiplier par 4 pour annualiser

**Acceptable** : Hardcoded `4` pour conversion période (pas une valeur légale).

---

### 5. Terminologie spécifique

| Concept | France | Tunisie |
|---------|--------|---------|
| Salaire minimum | SMIC | **SMIG** |
| Impôt | Taxe | **Impôt** (préférence) |
| Régime général | CNAV | **CNSS** (Caisse Nationale de Sécurité Sociale) |
| Fonction publique | CNRACL | **CNRPS** |
| Prestations familiales | AF | **AF** + majoration salaire unique + crèche |

#### "Salaire unique"
**Concept tunisien** : Majoration si un seul salaire dans le ménage.

```python
# prestations_familiales.py ligne 111-129
class majoration_salaire_unique(Variable):
    label = "Majoration du salaire unique"
    # ...
```

**Principe** : Famille avec 1 seul revenu → majoration des AF.

---

### 6. Monnaie et unités

- **Monnaie** : **TND** (Dinar Tunisien)
- **Périodes** : Mensuelles, trimestrielles, annuelles
- **Unités custom** : `unit: smig`, `threshold_unit: trimestre`

```yaml
# Exemple: bareme_annuite.yaml
metadata:
  threshold_unit: trimestre  # ✅ Unit personnalisée
  rate_unit: /1
```

---

### 7. Sources législatives

#### Sources principales
- **JORT** (Journal Officiel de la République Tunisienne) : [http://www.iort.gov.tn/](http://www.iort.gov.tn/)
- **CLEISS** : [http://www.cleiss.fr/docs/regimes/regime_tunisie_salaries.html](http://www.cleiss.fr/docs/regimes/regime_tunisie_salaries.html)
- **Code de sécurité sociale**
- **Code fiscal tunisien**

#### Langue
- **Français** et **Arabe**
- Privilégier versions françaises (communauté OpenFisca)
- Vérifier cohérence FR/AR si doute

---

### 8. Historique des paramètres

**Observation** : Historique très complet, certains depuis 1959.

**Exemple** : `bareme_annuite.yaml`
```yaml
brackets:
- threshold:
    1959-02-01: 0      # ✅ Depuis 1959 !
    1985-01-01: 40     # Évolution 1985
  rate:
    1959-02-01: 0.005
    1985-01-01: 0.0075
```

**Principe tunisien** : Conserver tout l'historique (simulations rétrospectives).

---

## Questions ouvertes (à résoudre)

### 1. ~~Hiérarchie paramètres~~ ✅ **RÉSOLU**

**Question** : Séparer CNSS et CNRPS ?

**Réponse** : ✅ OUI, déjà fait dans openfisca-tunisia :
```
retraite/
├── cnrps/  # Fonction publique
├── rsa/    # Salariés agricoles
└── rsna/   # Salariés non agricoles
```

**Pattern à suivre** : Respecter hiérarchie existante (voir section 1 ci-dessus).

---

### 2. SMIG comme unit - Acceptable ?

**Question** : `unit: smig` au lieu de `TND` ?

**Observation** : Utilisé dans openfisca-tunisia pour paramètres indexés sur SMIG.

**Décision temporaire** : ✅ **Acceptable** pour valeurs dérivées du SMIG.

**Raison** : Évite de dupliquer calculs (valeur évolue auto avec SMIG).

**Alternative** : Utiliser `formula` dans YAML (si supporté par OpenFisca Core).

---

### 3. Calculs trimestriels - Hardcoded `4` OK ?

**Observation** : `return 4 * af_base  # annualisé`

**Décision** : ✅ **Acceptable** (conversion de période, pas une valeur légale).

**Principe** : Hardcoded OK pour conversions mathématiques (0, 1, 4 trimestres, 12 mois).

---

### 4. TODO en production

**Observation** : Nombreux `# TODO` dans openfisca-tunisia.

**Décision** : ❌ **Pas acceptable** selon nos principes.

**Action** : Pour nouvelles implémentations, pas de TODO. Pour code existant : à nettoyer progressivement.

---

### 5. Références sans `#page=XX`

**Observation** : URLs sans numéro de page.

**Décision** : ⚠️ **À améliorer**.

**Action** : Nouvelles références → toujours ajouter `#page=XX` pour PDFs.

---

### 6. Nommage variables

**Question** : Suivre exactement openfisca-tunisia ou normaliser ?

**Décision** : ✅ **Suivre l'existant** pour cohérence.

**Principe** : Continuité > normalisation arbitraire.

---

### 7. Workflows spécifiques

**Question** : Validation manuelle nécessaire ?

**À déterminer** : Selon complexité du programme.

**Suggestion** : Validation manuelle pour retraite (3 régimes, historique complexe).

---

## Ressources

### Code existant
- **Repo** : [openfisca/openfisca-tunisia](https://github.com/openfisca/openfisca-tunisia)
- **Package Python** : `openfisca_tunisia`

### Documentation légale
- **JORT** : [http://www.iort.gov.tn/](http://www.iort.gov.tn/)
- **Code sécurité sociale** : [À compléter]
- **Code fiscal** : [À compléter]

### Experts
- Contacts : [À compléter]

---

## Checklist spécifique Tunisie

En plus de la [checklist universelle](../../01-universal/quality-checklist.md) :

- [ ] Vérifier cohérence version FR/AR des textes légaux (si doute)
- [ ] Montants en TND (pas EUR)
- [ ] Références JORT correctes (numéro, date, page)
- [ ] Distinction CNSS/CNRPS claire (si applicable)
- [ ] SMIG utilisé correctement pour valeurs dérivées
- [ ] (Futur) Métadonnées bilingues fr/ar quand OpenFisca Core le supportera

---

## Statistiques openfisca-tunisia

- **439 paramètres YAML** (très complet !)
- **40 fichiers variables Python**
- **Historique** : Paramètres depuis 1959
- **3 régimes retraite** distincts (CNRPS, RSA, RSNA)
- **Domaines couverts** : Impôt revenu, cotisations sociales, prestations familiales, retraite, énergie, TVA

---

## Conformité aux principes universels

| Principe | Conformité | Observations |
|----------|------------|--------------|
| Pas de hardcode | ✅ Respecté | Sauf conversions période (4, 12) |
| Paramètres documentés | ✅ Respecté | Metadata présente |
| Vectorisation | ✅ Respecté | max_, min_, where implicite |
| Entités correctes | ✅ Respecté | Menage, Individu, Foyer |
| Tests | ⚠️ Partiel | Tests présents mais à compléter |
| Pas de TODO | ❌ Non respecté | Nombreux TODO (à nettoyer) |
| Références avec #page | ⚠️ Partiel | Certaines références incomplètes |

**Conclusion** : Code existant **globalement conforme** aux principes, avec quelques améliorations possibles.

---

## Patterns tunisiens réutilisables

### 1. SMIG comme unité de référence
Paramètres indexés sur SMIG → `unit: smig` acceptable.

### 2. Calculs trimestriels
Pattern : `/4` → calcul → `*4` pour annualiser.

### 3. Barèmes avec historique complet
Conserver tout l'historique (simulations rétrospectives).

### 4. Trois régimes séparés
Si pays avec plusieurs régimes → hiérarchie distincte par régime.

### 5. Majoration salaire unique
Concept à vérifier si existe dans autres pays.

---

## Notes pour agents IA

- **Statut** : Pays de référence (premier implémenté)
- **Maturité** : ✅ Très mature (439 paramètres, historique depuis 1959)
- **Couverture** : ✅ Très complète (impôts, cotisations, prestations, retraite)
- **Documentation** : Voir [config/countries/tunisia.yaml](../../../../config/countries/tunisia.yaml) et [docs/agents/02-framework/country-config.md](../../02-framework/country-config.md)

**Recommandation** : Utiliser openfisca-tunisia comme **référence** pour nouveaux agents et nouvelles implémentations.

---

_Document enrichi le 2026-03-11 après analyse d'openfisca-tunisia._
