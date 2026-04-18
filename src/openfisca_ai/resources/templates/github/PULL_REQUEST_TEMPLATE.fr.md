Merci de contribuer à {{project_name}} ! Effacez les lignes ne correspondant pas à votre contribution.

* Évolution réglementaire. | Amélioration technique. | Correction d'un bug. | Changement mineur.
* Zones impactées : `chemin/vers/les/fichiers/modifiés`.
* Détails :
  - Description du changement apporté.
  - Cas dans lesquels une erreur était constatée (si correction).

- - - -

Checklist :

- [ ] J'ai consulté le [guide de contribution](CONTRIBUTING.md).
- [ ] J'ai vérifié qu'il n'existe pas de [PR similaire](../../pulls).
- [ ] J'ai validé avec `openfisca-ai` : `uv run openfisca-ai validate-parameters .`
- [ ] J'ai ajouté ou mis à jour les tests correspondants.
- [ ] Les tests passent : `uv run pytest`.
- [ ] J'ai mis à jour le [`CHANGELOG.md`](CHANGELOG.md).
