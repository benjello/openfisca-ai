#!/usr/bin/env python3
"""Generate CI workflow files for an OpenFisca country package.

Detects the package structure, runs an audit, then writes GitHub Actions
and GitLab CI workflow files tailored to the repository.

Usage:
  openfisca-ai setup-ci <package-path> [--dry-run] [--github] [--gitlab] [--force]
"""

from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent


def detect_package_info(repo_path: Path) -> dict:
    """Detect package name, parameter path, default branch, python versions."""
    repo_path = repo_path.resolve()

    package_dir = None
    for child in repo_path.iterdir():
        if (
            child.is_dir()
            and child.name.startswith("openfisca_")
            and (child / "__init__.py").exists()
        ):
            package_dir = child
            break

    package_name = package_dir.name if package_dir else repo_path.name
    display_name = package_name.replace("_", "-").replace("openfisca-", "OpenFisca-")

    param_path = None
    if package_dir:
        candidate = package_dir / "parameters"
        if candidate.is_dir():
            param_path = f"{package_dir.name}/parameters"

    pyproject = repo_path / "pyproject.toml"
    python_versions = ["3.10", "3.11", "3.12"]
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        for line in text.splitlines():
            if "python_requires" in line or "requires-python" in line:
                if "3.11" in line:
                    python_versions = ["3.11", "3.12"]
                elif "3.12" in line:
                    python_versions = ["3.12"]

    default_branch = "master"
    head_ref = repo_path / ".git" / "HEAD"
    if head_ref.exists():
        content = head_ref.read_text().strip()
        if content.startswith("ref: refs/heads/"):
            candidate_branch = content.split("/")[-1]
            if candidate_branch in ("main", "master"):
                default_branch = candidate_branch

    main_ref = repo_path / ".git" / "refs" / "heads" / "main"
    master_ref = repo_path / ".git" / "refs" / "heads" / "master"
    if main_ref.exists() and not master_ref.exists():
        default_branch = "main"

    has_openfisca_ai = False
    if pyproject.exists():
        has_openfisca_ai = "openfisca-ai" in pyproject.read_text(encoding="utf-8")

    has_makefile = (repo_path / "Makefile").exists()

    test_yaml_count = len(list(repo_path.rglob("tests/**/*.yaml")))
    test_py_count = len([
        p for p in repo_path.rglob("tests/**/*.py")
        if p.name not in ("__init__.py", "conftest.py")
    ])

    return {
        "repo_path": repo_path,
        "package_name": package_name,
        "display_name": display_name,
        "param_path": param_path,
        "python_versions": python_versions,
        "default_branch": default_branch,
        "has_openfisca_ai": has_openfisca_ai,
        "has_makefile": has_makefile,
        "test_yaml_count": test_yaml_count,
        "test_py_count": test_py_count,
    }


def generate_github_validate_workflow(info: dict) -> str:
    """Generate .github/workflows/validate.yml for openfisca-ai checks."""
    return dedent(f"""\
        name: Validate with openfisca-ai

        on:
          push:
          pull_request:
            types: [opened, reopened, synchronize]

        jobs:
          validate:
            runs-on: ubuntu-24.04
            steps:
              - uses: actions/checkout@v4
              - uses: actions/setup-python@v5
                with:
                  python-version: "{info['python_versions'][-1]}"
              - uses: astral-sh/setup-uv@v4
              - name: Install dependencies
                run: uv sync --extra dev
              - name: Validate code (informational)
                run: uv run openfisca-ai validate-code . || true
              - name: Validate parameters (informational)
                run: uv run openfisca-ai validate-parameters . || true
              - name: Validate units (informational)
                run: uv run openfisca-ai validate-units . || true
              - name: Full audit (informational)
                run: uv run openfisca-ai audit . --markdown --output audit-report.md || true
              - name: Upload audit report
                if: always()
                uses: actions/upload-artifact@v4
                with:
                  name: openfisca-ai-audit
                  path: audit-report.md
    """)


def generate_github_review_workflow(info: dict) -> str:
    """Generate .github/workflows/ai-review.yml for LLM-powered PR review."""
    return dedent(f"""\
        name: AI Review

        on:
          pull_request:
            types: [opened, reopened, synchronize]

        permissions:
          pull-requests: write
          contents: read

        jobs:
          review:
            runs-on: ubuntu-24.04
            if: github.event.pull_request.draft == false
            steps:
              - uses: actions/checkout@v4
                with:
                  fetch-depth: 0
              - uses: actions/setup-python@v5
                with:
                  python-version: "{info['python_versions'][-1]}"
              - uses: astral-sh/setup-uv@v4
              - name: Install dependencies
                run: uv sync --extra dev
              - name: Pre-digest and review
                env:
                  ANTHROPIC_API_KEY: ${{{{ secrets.ANTHROPIC_API_KEY }}}}
                  OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
                  GEMINI_API_KEY: ${{{{ secrets.GEMINI_API_KEY }}}}
                run: |
                  git diff origin/${{{{ github.base_ref }}}}...HEAD > pr.diff
                  uv run openfisca-ai review-diff . --diff-file pr.diff --json > review-digest.json
                  uv run openfisca-ai review-diff . --diff-file pr.diff --markdown > review-digest.md
                  uv run python -m openfisca_ai.tools.ci_review --digest review-digest.json --digest-md review-digest.md --diff pr.diff --output review.md
              - name: Post review comment
                env:
                  GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
                run: |
                  BODY="## Review automatique openfisca-ai

                  $(cat review.md)"
                  gh pr comment ${{{{ github.event.pull_request.number }}}} --body "$BODY" 2>/dev/null || echo "Could not post comment"
    """)


def generate_github_changelog_workflow(info: dict) -> str:
    """Generate .github/workflows/auto-changelog.yml for automated changelog."""
    return dedent(f"""\
        name: Auto Changelog

        on:
          pull_request:
            types: [closed]

        permissions:
          contents: write
          pull-requests: read

        jobs:
          changelog:
            runs-on: ubuntu-24.04
            if: github.event.pull_request.merged == true && secrets.ANTHROPIC_API_KEY != ''
            steps:
              - uses: actions/checkout@v4
                with:
                  ref: {info['default_branch']}
                  fetch-depth: 0
              - name: Generate changelog entry
                env:
                  ANTHROPIC_API_KEY: ${{{{ secrets.ANTHROPIC_API_KEY }}}}
                  GH_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
                run: |
                  python - <<'PYEOF'
          import json, os, subprocess

          pr_number = "{{}}"  # filled at runtime
          pr_title = os.environ.get("PR_TITLE", "")
          diff = subprocess.check_output(
              ["git", "diff", "HEAD~1...HEAD"], text=True
          )

          prompt = f\"\"\"Génère une entrée CHANGELOG en français pour cette PR mergée.

          Titre : {{pr_title}}
          Diff (extrait) :
          ```
          {{diff[:8000]}}
          ```

          Format attendu (une seule section parmi Ajouté/Modifié/Corrigé/Supprimé) :
          ### Ajouté|Modifié|Corrigé|Supprimé
          - Description concise du changement.

          Réponds UNIQUEMENT avec l'entrée CHANGELOG, rien d'autre.\"\"\"

          try:
              import anthropic
              client = anthropic.Anthropic()
              response = client.messages.create(
                  model="claude-haiku-4-5-20251001",
                  max_tokens=256,
                  messages=[{{"role": "user", "content": prompt}}],
              )
              entry = response.content[0].text.strip()
          except Exception as e:
              entry = f"- PR mergée (changelog auto indisponible : {{e}})"

          with open("changelog_entry.md", "w") as f:
              f.write(entry)
          print(entry)
          PYEOF
              - name: Upload changelog entry
                uses: actions/upload-artifact@v4
                with:
                  name: changelog-entry
                  path: changelog_entry.md
    """)


def generate_gitlab_ci(info: dict) -> str:
    """Generate .gitlab-ci.yml for GitLab CI."""
    py_version = info["python_versions"][-1]
    return dedent(f"""\
        stages:
          - validate
          - test
          - review

        variables:
          PYTHON_VERSION: "{py_version}"

        .uv-setup: &uv-setup
          image: python:${{PYTHON_VERSION}}
          before_script:
            - pip install uv
            - uv sync --extra dev

        validate:
          <<: *uv-setup
          stage: validate
          script:
            - uv run openfisca-ai validate-parameters .
            - uv run openfisca-ai validate-units .
            - uv run openfisca-ai validate-code .
            - uv run openfisca-ai audit . --markdown --output audit-report.md
          artifacts:
            paths:
              - audit-report.md
            when: always

        test:
          <<: *uv-setup
          stage: test
          script:
            - uv run pytest
          parallel:
            matrix:
              - PYTHON_VERSION: [{", ".join(f'"{v}"' for v in info["python_versions"])}]

        ai-review:
          <<: *uv-setup
          stage: review
          rules:
            - if: $CI_PIPELINE_SOURCE == "merge_request_event" && $ANTHROPIC_API_KEY
          script:
            - uv run openfisca-ai audit . --json --output audit.json
            - git diff ${{CI_MERGE_REQUEST_DIFF_BASE_SHA}}...${{CI_COMMIT_SHA}} > mr.diff
            - |
              python - <<'PYEOF'
              import json, os

              diff = open("mr.diff").read()
              audit = open("audit.json").read()

              prompt = f\"\"\"Tu es un relecteur expert OpenFisca. Analyse ce diff et le rapport d'audit.

              ## Rapport d'audit
              {{audit}}

              ## Diff
              ```diff
              {{diff[:15000]}}
              ```

              Produis une review concise en français :
              1. Résumé (2-3 lignes)
              2. Problèmes détectés
              3. Suggestions
              4. Verdict\"\"\"

              try:
                  import anthropic
                  client = anthropic.Anthropic()
                  response = client.messages.create(
                      model="claude-haiku-4-5-20251001",
                      max_tokens=1024,
                      messages=[{{"role": "user", "content": prompt}}],
                  )
                  review = response.content[0].text
              except Exception as e:
                  review = f"Review indisponible : {{e}}"

              with open("review.md", "w") as f:
                  f.write(review)
              print(review)
              PYEOF
          artifacts:
            paths:
              - review.md
            when: always
    """)


def setup_ci(repo_path: Path, *, dry_run: bool = False, github: bool = True, gitlab: bool = True, force: bool = False) -> dict:
    """Detect package info and generate CI files."""
    info = detect_package_info(repo_path)

    files = {}

    if github:
        gh_dir = repo_path / ".github" / "workflows"
        files[gh_dir / "validate.yml"] = generate_github_validate_workflow(info)
        files[gh_dir / "ai-review.yml"] = generate_github_review_workflow(info)
        files[gh_dir / "auto-changelog.yml"] = generate_github_changelog_workflow(info)

    if gitlab:
        files[repo_path / ".gitlab-ci.yml"] = generate_gitlab_ci(info)

    written = []
    skipped = []

    for path, content in files.items():
        if path.exists() and not force:
            skipped.append(str(path))
            continue

        if dry_run:
            written.append(str(path))
            continue

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path))

    return {
        "info": {k: str(v) if isinstance(v, Path) else v for k, v in info.items()},
        "written": written,
        "skipped": skipped,
        "dry_run": dry_run,
    }


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: openfisca-ai setup-ci <package-path> [--dry-run] [--github] [--gitlab] [--force]")
        sys.exit(1)

    repo_path = Path(args[0])
    if not repo_path.exists():
        print(f"Path not found: {repo_path}")
        sys.exit(1)

    dry_run = "--dry-run" in args
    force = "--force" in args

    explicit_github = "--github" in args
    explicit_gitlab = "--gitlab" in args
    if not explicit_github and not explicit_gitlab:
        github = True
        gitlab = True
    else:
        github = explicit_github
        gitlab = explicit_gitlab

    result = setup_ci(repo_path, dry_run=dry_run, github=github, gitlab=gitlab, force=force)
    info = result["info"]

    print(f"Package: {info['display_name']}")
    print(f"  Package dir: {info['package_name']}")
    print(f"  Parameters: {info['param_path'] or 'not found'}")
    print(f"  Python: {', '.join(info['python_versions'])}")
    print(f"  Branch: {info['default_branch']}")
    print(f"  Tests: {info['test_yaml_count']} YAML, {info['test_py_count']} Python")
    print(f"  openfisca-ai in deps: {'yes' if info['has_openfisca_ai'] else 'no'}")
    print()

    if dry_run:
        print("Dry run — files that would be written:")
    else:
        print("Files written:")

    for f in result["written"]:
        print(f"  + {f}")
    for f in result["skipped"]:
        print(f"  ~ {f} (exists, use --force to overwrite)")

    if not result["written"] and not result["skipped"]:
        print("  (none)")


if __name__ == "__main__":
    main()
