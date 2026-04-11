# Spécificités pays : [NOM_PAYS]

Aménagements à la norme OpenFisca AI pour [NOM_PAYS].

## Vue d'ensemble

Ce fichier documente les **déviations** par rapport aux [principes universels](../01-universal/principles.md) et au [framework standard](../02-framework/).

**Si votre pays suit la norme sans aménagement** → ce fichier peut rester vide ou minimal.

---

## Configuration

Voir `config/countries/[pays_id].yaml` pour la configuration technique (chemins, hiérarchie, conventions).

---

## Aménagements

### 1. Nomenclature et conventions

**Si différent du standard (snake_case)** :

#### Nommage des variables
```yaml
# Dans config/countries/[pays_id].yaml
conventions:
  naming: camelCase  # ou snake_case, PascalCase
```

Exemple :
- Standard : `allocation_logement`
- Aménagement : `allocationLogement` (si camelCase pour ce pays)

**Raison** : [Expliquer pourquoi, ex: cohérence avec code existant du pays]

---

#### Terminologie

Termes spécifiques au pays à utiliser partout :

| Concept | Standard | Ce pays |
|---------|----------|---------|
| Impôt | `taxe` | `impot` |
| Allocations | `benefits` | `prestations` |
| Salaire | `salary` | `salaire` |

**Raison** : [Cohérence avec législation locale, code existant, etc.]

---

### 2. Hiérarchie de paramètres

**Si différent de la hiérarchie standard** :

```yaml
# Standard suggéré
parameter_hierarchy:
  - gov
  - social_security
  - taxation

# Aménagement pour ce pays
parameter_hierarchy:
  - gouvernement
  - securite_sociale
  - impots
  - autres
```

**Raison** : [Ex: structure du code existant, organisation administrative du pays]

---

### 3. Entités

**Si entités spécifiques** :

```yaml
# Standard OpenFisca
entity_levels:
  - Person
  - Famille
  - Foyer
  - Menage

# Aménagement pour ce pays
entity_levels:
  - Individu        # Au lieu de Person
  - Famille
  - FoyerFiscal     # Au lieu de Foyer
  - Menage
  - Entreprise      # Entité supplémentaire
```

**Raison** : [Ex: législation locale définit "Foyer Fiscal" différemment]

---

### 4. Workflows spécifiques

**Si workflow modifié pour ce pays** :

#### Validation manuelle obligatoire

Pour certains programmes sensibles (ex: système de retraite), validation manuelle obligatoire avant commit.

**Programmes concernés** :
- `retraite_*`
- `pension_invalidite`

**Workflow** :
1. Implémentation (rules-engineer)
2. Tests automatiques (test-creator)
3. **⚠️ Validation manuelle expert pays** (avant validators automatiques)
4. Validators automatiques
5. Commit

**Raison** : [Ex: Complexité réglementaire, risque élevé d'erreur]

---

#### Sources spécifiques

Sources législatives dans une langue non-standard ou format particulier :

- **Langue** : [Ex: Arabe + Français pour Tunisie]
- **Format** : [Ex: PDFs scannés nécessitant OCR]
- **Accès** : [Ex: certains textes non publics, nécessitent authentification]

**Actions document-collector** :
- [Instructions spécifiques, ex: "Utiliser OCR pour PDFs scannés"]
- [URLs d'accès particulières]

---

### 5. Règles non-simulables spécifiques

**Règles de ce pays** identifiées comme **non-simulables** :

| Programme | Règle | Raison |
|-----------|-------|--------|
| [Programme X] | [Description règle] | [Pourquoi non-simulable] |

Exemple :
| Allocation chômage | Historique 5 dernières années | Nécessite données historiques indisponibles |

**Action** : Signaler clairement dans la doc et les tests.

---

### 6. Valeurs dérivées spécifiques

**Paramètres calculés** à partir d'autres (spécifiques à ce pays) :

```yaml
# Exemple : Plafond = 2 × SMIG (Tunisie)
plafond_allocation:
  formula: gov.smig * 2
  description: Plafond basé sur 2 fois le SMIG.
  reference: "Loi n° 2020-15, Art. 47"
```

**Liste des dépendances** :
- `smig` → utilisé par `plafond_allocation`, `seuil_pauvrete`
- [Autres]

---

### 7. Tests et validation

**Si critères de validation différents** :

#### Couverture de tests
- Standard : 80%
- Ce pays : **90%** (programmes sensibles)

**Raison** : [Ex: Exigence réglementaire]

#### Calculateurs de référence
- **URL** : [Lien vers calculateur officiel du pays]
- **Usage** : Tous les tests d'intégration doivent être validés contre ce calculateur

---

### 8. Performance et optimisations

**Si contraintes spécifiques** :

- **Taille population** : [Ex: 100M habitants → optimisation critique]
- **Fréquence calculs** : [Ex: calculs quotidiens pour API publique]
- **Optimisations requises** : [Ex: cache agressif, pré-calculs]

---

### 9. Intégration avec systèmes existants

**Si API ou systèmes spécifiques** :

- **API gouvernementale** : [URL, documentation]
- **Format d'échange** : [Ex: JSON, XML]
- **Authentification** : [Méthode]

---

## Exemples concrets

### Exemple 1 : [Nom du programme]

#### Particularité
[Description de l'aménagement]

#### Implémentation
```python
# Code spécifique avec commentaires
```

#### Raison
[Pourquoi cet aménagement est nécessaire]

---

## Checklist spécifique pays

En plus de la [checklist universelle](../01-universal/quality-checklist.md) :

- [ ] [Critère spécifique 1]
- [ ] [Critère spécifique 2]
- [ ] [...]

---

## Ressources pays

- **Code existant** : [Lien repo GitHub openfisca-[pays]]
- **Documentation législative** : [URL portail légal]
- **Contact expert pays** : [Email/lien]
- **Forum/communauté** : [Lien]

---

## Notes

[Toute autre information pertinente spécifique à ce pays]
