# Reusable templates for OpenFisca packages

This directory contains generic contribution templates that any OpenFisca country
or city package can adapt. Each template is available in French (`.fr.md`) and
English (`.en.md`).

## Structure

```
templates/
  contributing/          # CONTRIBUTING.md templates
  github/                # GitHub issue & PR templates
  gitlab/
    issue_templates/     # GitLab issue templates (bug, feature)
    merge_request_templates/  # GitLab MR templates
```

## Usage

1. Copy the templates matching your language into your repository.
2. Replace `{{project_name}}` with your project name (e.g. "OpenFisca-France").
3. Replace `{{project_slug}}` with your directory name (e.g. "openfisca-france").
4. Add domain-specific sections (grade/filière for Paris-RH, prestations for France, etc.).
5. Place GitHub templates under `.github/` and GitLab templates under `.gitlab/`.
