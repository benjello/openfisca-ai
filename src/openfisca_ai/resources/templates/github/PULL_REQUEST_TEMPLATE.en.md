Thank you for contributing to {{project_name}}! Delete the lines that do not apply to your contribution.

* Regulatory update. | Technical improvement. | Bug fix. | Minor change.
* Impacted areas: `path/to/modified/files`.
* Details:
  - Description of the change.
  - Cases where an error was observed (if fix).

- - - -

Checklist:

- [ ] I have read the [contributing guide](CONTRIBUTING.md).
- [ ] I have checked that no [similar PR](../../pulls) exists.
- [ ] I have validated with `openfisca-ai`: `uv run openfisca-ai validate-parameters .`
- [ ] I have added or updated the relevant tests.
- [ ] Tests pass: `uv run pytest`.
- [ ] I have updated [`CHANGELOG.md`](CHANGELOG.md).
