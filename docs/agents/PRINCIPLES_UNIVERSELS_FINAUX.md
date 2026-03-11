# Principes Universels OpenFisca - Version Finale

Principes applicables à **tous les pays**, **tous les agents**, **toutes les tâches**.

**Validés par** : Analyse d'openfisca-tunisia (439 paramètres, 40 variables, historique depuis 1959).

---

## 🔐 Les 14 Principes Universels

### Groupe 1 : Source et vérité (3)

#### 1. La loi est la source de vérité
- **Toujours** se référer aux textes officiels
- **Jamais** deviner une règle ou une valeur
- **Chercher** avant d'implémenter

**Exemple** :
```python
# ✅ BON
reference = "Loi n° 2020-15, Article 46"
```

---

#### 2. Zéro valeur en dur
- **Aucune** valeur légale dans le code Python
- **Toutes** les valeurs viennent des paramètres YAML
- **Exceptions** : 0, 1, conversions période (4 trimestres, 12 mois)

**Exemple** :
```python
# ❌ MAUVAIS
montant = 1500  # Valeur en dur !

# ✅ BON
montant = parameters(period).prestations.plafond_revenu

# ✅ ACCEPTABLE : Conversion période
return 4 * montant_trimestriel  # 4 = nombre de trimestres (conversion)
```

---

#### 3. Références précises
- **URLs** avec `#page=XX` pour PDFs
- **Citations** exactes (loi, article, date)
- **Sources** vérifiables

**Exemple** :
```yaml
reference:
  - "Loi n° 2020-15, Article 46"
  - "https://example.gov/loi-2020-15.pdf#page=12"  # ✅ Avec #page=XX
```

---

### Groupe 2 : Paramètres (4)

#### 4. Paramètres bien documentés
**Obligatoire** :
- `description` : Une phrase claire
- `label` : Nom court pour UI
- `reference` : URL ou citation légale
- `unit` : `/1`, `EUR`, `TND`, etc.

**Exemple** :
```yaml
plafond_revenu:
  description: Plafond de revenu mensuel pour l'éligibilité à l'allocation logement.
  label: Plafond revenu
  reference: "https://example.gov/loi.pdf#page=12"
  unit: TND
  values:
    2020-01-01: 1500
```

---

#### 5. Historique complet
- **Conserver** toutes les valeurs passées
- **Permet** simulations rétrospectives
- **Format** : `date: valeur`

**Exemple** :
```yaml
values:
  1959-02-01: 0.005    # ✅ Depuis 1959
  1985-01-01: 0.0075   # Évolution 1985
  2024-01-01: 0.010    # Valeur actuelle
```

---

#### 6. Valeurs indexées acceptables
- **Indexation** sur référence (SMIG, SMIC, inflation) → `unit: <reference>`
- **Évolution** automatique avec la référence
- **Alternative** : `formula` dans YAML

**Exemple** :
```yaml
pension_minimale:
  description: Pension minimale (2/3 du SMIG)
  unit: smig  # ✅ Valeur indexée sur SMIG
  values:
    1974-01-01: 0.66666  # = 2/3 SMIG
```

---

#### 7. Metadata extensible
- **Standard** : description, label, reference, unit
- **Custom** : Champs additionnels selon besoins
- **Exemples** : `threshold_unit: trimestre`, `rate_unit: /1`

**Exemple** :
```yaml
bareme:
  brackets: [...]
  metadata:
    threshold_unit: trimestre  # ✅ Custom
    rate_unit: /1
```

---

### Groupe 3 : Code (4)

#### 8. Entités correctes
- **Selon la loi** : Person, Famille, Foyer, Menage
- **Vérifier** quel niveau reçoit/calcule la prestation
- **Ne pas deviner**

**Exemple** :
```python
class allocation_logement(Variable):
    entity = Famille  # ✅ La loi dit "famille"
```

---

#### 9. Vectorisation
- **where()**, **max_()**, **min_()** au lieu de boucles
- **NumPy** pour performances
- **Pas** de `for` ou `if` explicites

**Exemple** :
```python
# ❌ MAUVAIS
for person in persons:
    if person.age > 18:
        result[person] = calcul(person)

# ✅ BON
eligible = age > 18
result = where(eligible, calcul(...), 0)
```

---

#### 10. Conversions période acceptables
- **4** (trimestres), **12** (mois) acceptables
- **Documenter** en commentaire
- **Pas** une valeur légale (conversion mathématique)

**Exemple** :
```python
# ✅ ACCEPTABLE
return 4 * montant_trimestriel  # 4 trimestres dans l'année
return 12 * montant_mensuel     # 12 mois dans l'année
```

---

#### 11. Pas de TODO en production
- **Nouveau code** : Zéro TODO
- **Code legacy** : Nettoyer progressivement
- **Principe** : Code complet ou ne pas commiter

**Exemple** :
```python
# ❌ MAUVAIS
def formula(...):
    # TODO: ajouter éligibilité
    return montant

# ✅ BON
def formula(...):
    eligible = revenu < plafond  # Complet
    return where(eligible, montant, 0)
```

---

### Groupe 4 : Qualité (3)

#### 12. Tests systématiques
- **Chaque variable** avec formule → test
- **Cas nominaux** + **cas limites**
- **Calculs manuels** en commentaires

**Exemple** :
```python
def test_allocation_eligible():
    """
    Calcul manuel (Loi 2020-15, Art. 46, p.12) :
    - Revenu : 1200 TND (< plafond 1500)
    - Montant : 200 TND
    → Allocation = 200 TND
    """
    simulation.set_input('revenu', 1200)
    assert simulation.calculate('allocation') == 200
```

---

#### 13. Réutilisation de patterns
- **Étudier** code existant du pays
- **Réutiliser** patterns cohérents
- **Éviter** duplication

**Exemple** :
- Pattern calcul trimestriel (Tunisia)
- Pattern éligibilité revenu
- Pattern barème progressif

---

#### 14. Formatage
- **Python** : Black
- **YAML** : Prettier ou yamllint
- **Cohérence** dans tout le projet

---

## 📊 Tableau récapitulatif

| Groupe | Principes | Validation |
|--------|-----------|------------|
| **Source et vérité** | 1-3 | ✅ Validés par Tunisia |
| **Paramètres** | 4-7 | ✅ Validés + 3 nouveaux découverts |
| **Code** | 8-11 | ✅ Validés avec nuances |
| **Qualité** | 12-14 | ✅ Validés (application partielle) |

---

## 🌍 Ce qui N'est PAS universel

**Configuration par pays** (voir `config/countries/<pays>.yaml`) :
- Hiérarchie de paramètres
- Nommage des entités
- Monnaie
- Terminologie (SMIG vs SMIC, impôt vs taxe)
- Régimes distincts (CNRPS/RSA/RSNA en Tunisie)
- Périodes de calcul (trimestriel vs mensuel)

---

## ✅ Checklist pré-commit

Avant tout commit, vérifier :

- [ ] **Principe 1** : Basé sur texte officiel (pas deviné)
- [ ] **Principe 2** : Pas de hardcode (sauf 0, 1, 4, 12)
- [ ] **Principe 3** : Références avec #page=XX
- [ ] **Principe 4** : Paramètres avec description, label, reference, unit
- [ ] **Principe 5** : Historique des valeurs présent
- [ ] **Principe 8** : Entité correcte
- [ ] **Principe 9** : Code vectorisé
- [ ] **Principe 11** : Pas de TODO
- [ ] **Principe 12** : Tests écrits et qui passent
- [ ] **Principe 14** : Code formaté

---

## 📚 Ressources

- **Validation** : [UNIVERSAL_PRINCIPLES_VALIDATION.md](UNIVERSAL_PRINCIPLES_VALIDATION.md)
- **Apprentissage** : [LEARNING_LOG.md](../LEARNING_LOG.md)
- **Guide détaillé** : [01-universal/principles.md](01-universal/principles.md)
- **Exemple pays** : [03-countries/tunisia/specifics.md](03-countries/tunisia/specifics.md)

---

**Version** : 1.0 (2026-03-11)
**Validés par** : openfisca-tunisia
**Statut** : ✅ Finalisés et applicables
