# Learning Log - OpenFisca Tunisia

Journal d'apprentissage des principes généraux et spécificités tunisiennes.

## 📊 Statistiques

- **439 paramètres YAML** (très complet !)
- **40 fichiers variables Python**
- **Historique** : Certains paramètres depuis 1959
- **Dernière mise à jour** : Mars 2025

---

## ✅ Principes généraux observés

### 1. Pas de hardcode ✅
**Exemple** : `prestations_familiales.py` ligne 97-98
```python
bm = min_(
    max_(...) / 4,
    pf.af.plaf_trim,  # ✅ Vient des paramètres
)
```

### 2. Vectorisation ✅
**Exemple** : `prestations_familiales.py` ligne 104-107
```python
af_base = (
    (af_nbenf >= 1) * af_1enf +  # Conditions vectorisées
    (af_nbenf >= 2) * af_2enf +
    (af_nbenf >= 3) * af_3enf
)
```

### 3. Entités correctes ✅
- `af` (allocations familiales) → `Menage`
- `prestations_familiales_enfant_a_charge` → `Individu`

### 4. Barèmes avec historique ✅
**Exemple** : `bareme_annuite.yaml`
```yaml
brackets:
- threshold:
    1959-02-01: 0
    1985-01-01: 40  # Évolution des seuils dans le temps
  rate:
    1959-02-01: 0.005
    1985-01-01: 0.0075
```

### 5. Metadata présente ✅
```yaml
metadata:
  threshold_unit: trimestre
  rate_unit: /1
```

---

## ⚠️ Écarts avec nos principes (à améliorer)

### 1. TODO présents (à supprimer)
**Fichier** : `prestations_familiales.py`
- Ligne 42 : `# TODO`
- Ligne 50 : `# TODO à retravailler`
- Ligne 89 : `# TODO: ajouter éligibilité`
- Ligne 160 : `# TODO rework and test`
- Ligne 191 : `# TODO add _af_cong_naiss`

❌ **Principe** : Pas de TODO en production

### 2. Références sans `#page=XX`
```python
reference = "http://www.cleiss.fr/docs/regimes/regime_tunisie_salaries.html"
```
⚠️ **Amélioration** : Ajouter `#page=XX` si c'est un PDF

### 3. Unit non-standard
**Fichier** : `minimum_garanti.yaml`
```yaml
unit: smig  # ⚠️ Devrait être TND ou utiliser formula
```

### 4. Hardcoded `4` pour annualisation
```python
return 4 * af_base  # annualisé
```
✅ **Acceptable** (conversion de période), mais pourrait être documenté dans un paramètre

---

## 🌍 Spécificités tunisiennes identifiées

### 1. Hiérarchie des paramètres
**Observation** : Hiérarchie très détaillée et spécifique Tunisie

```
parameters/
├── energie/
├── fiscalite_indirecte/
├── impot_revenu/
│   ├── bic/  # Bénéfices industriels et commerciaux
│   ├── bnc/  # Bénéfices non commerciaux
│   ├── tspr/ # Taxe spéciale ?
│   └── ...
├── marche_travail/
├── prelevements_sociaux/
├── prestations/
│   ├── contributives/
│   └── non_contributives/
└── retraite/
    ├── cnrps/  # Fonction publique
    ├── rsa/    # Salariés agricoles
    └── rsna/   # Salariés non agricoles
```

**À documenter** : Distinction CNRPS/RSA/RSNA importante pour la Tunisie.

### 2. SMIG (Salaire Minimum Interprofessionnel Garanti)
- Équivalent du SMIC français
- Utilisé comme référence (`unit: smig`)
- SMIG 48h vs SMIG 40h (selon secteur)

**Exemple** : `prestations_familiales.py` ligne 158-160
```python
smig48 = parameters(period.start).marche_travail.smig_48h_mensuel
```

### 3. Trois régimes de retraite distincts
- **CNRPS** : Caisse Nationale de Retraite et de Prévoyance Sociale (fonction publique)
- **RSA** : Régime Salariés Agricoles
- **RSNA** : Régime Salariés Non Agricoles

**Impact** : Paramètres séparés par régime.

### 4. Terminologie
- **"Salaire unique"** : Concept spécifique Tunisie (majoration si un seul salaire dans le ménage)
- **"SMIG"** plutôt que "SMIC"
- **"Prestations familiales"** : allocations familiales + majoration salaire unique + frais crèche

### 5. Périodes trimestrielles
**Observation** : Beaucoup de calculs trimestriels (ligne 87, 97)
```python
# Le montant trimestriel est calculé...
bm = ... / 4  # base trimestrielle
return 4 * af_base  # annualisé
```

### 6. Sources légales
- **CLEISS** : Centre des Liaisons Européennes et Internationales de Sécurité Sociale
- **JORT** : Journal Officiel de la République Tunisienne (mentionné dans specifics.md)

### 7. Monnaie
- **TND** : Dinar Tunisien (pas EUR)
- Attention aux conversions et références

---

## 📝 Actions à prendre

### Court terme
1. **Mettre à jour `tunisia/specifics.md`** avec ces découvertes
2. **Valider principes universels** avec ces exemples concrets
3. **Configurer `tunisia.yaml`** avec chemins réels vers openfisca-tunisia

### Moyen terme
4. **Créer exemples tunisiens** dans les guides agents
5. **Proposer améliorations** : supprimer TODOs, ajouter #page=XX
6. **Documenter patterns** : calculs trimestriels, SMIG comme unité

### Long terme
7. **Généraliser** : Identifier patterns réutilisables pour autres pays
8. **Template** : Créer template pour ajouter un nouveau pays basé sur apprentissage Tunisie

---

## 🔍 Questions ouvertes

1. **SMIG comme unit** : Est-ce acceptable ou faut-il convertir en TND ?
2. **Calculs trimestriels** : Pattern à documenter comme convention pays ?
3. **CNRPS/RSA/RSNA** : Faut-il séparer dans hiérarchie paramètres comme actuellement ?
4. **Références CLEISS** : Acceptable ou préférer sources tunisiennes directes ?

---

## 📅 Prochaines étapes

- [ ] Lire plus de fichiers variables (impot_revenu, prelevements_sociaux)
- [ ] Analyser tests pour voir patterns de test
- [ ] Comparer avec doc OpenFisca officielle
- [ ] Identifier patterns réutilisables vs spécifiques Tunisie

---

_Log créé le 2026-03-11 par analyse d'openfisca-tunisia_
