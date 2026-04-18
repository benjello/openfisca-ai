#!/usr/bin/env python3
"""Bootstrap a units.yaml file for an OpenFisca country package.

Scans parameter files, detects units already declared, infers missing units
from filenames and descriptions via pattern matching (no LLM), and generates
a complete units.yaml.  Optionally annotates parameter files with `unit:`.

Usage:
  openfisca-ai init-units <package-path> [--apply] [--currency NAME SHORT]
  openfisca-ai init-units /path/to/openfisca-paris-rh --currency Euro €
  openfisca-ai init-units /path/to/openfisca-tunisia --currency Dinar DT
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import yaml


def _looks_like_date(key: str) -> bool:
    """Check if a key looks like a YYYY-MM-DD date."""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(key)))


# ---------------------------------------------------------------------------
# Pattern-based unit inference (order matters: first match wins)
# ---------------------------------------------------------------------------

UNIT_PATTERNS: list[tuple[str, str]] = [
    # Ratios / taux / coefficients
    (r"taux|ratio|pourcent|coefficient|majoration|reduction|part|proportion|quotient|prorata", "/1"),
    # Indices (indice brut, majoré, etc.)
    (r"indice|indice_brut|indice_majore|rang_classement", "index_point"),
    # Durées
    (r"duree_mois|mois_min|mois_max|anciennete.*mois", "month"),
    (r"duree|anciennete|annee|ans_min|ans_max", "year"),
    (r"trimestre|trimestriel", "trimestre"),
    (r"jour|day|jours", "day"),
    # Monétaire
    (r"montant|plafond|plancher|seuil|pension|salaire|prime|allocation|prestation|revenu|indemnite|prix|cout|tarif|valeur_point", "currency"),
    # Âge
    (r"age_", "year"),
    # Échelons / numéros
    (r"echelon|nb_echelon|nombre|effectif|rang", "integer"),
    # Catégories / listes
    (r"categorie|liste|type|code", "enum"),
    # Booléens encodés
    (r"hors_echelle|est_|flag|actif", "boolean"),
]


def _infer_unit(filepath: Path, description: str) -> str | None:
    """Infer a unit from the file path and description using patterns."""
    haystack = f"{filepath.stem} {filepath.parent.name} {description}".lower()
    for pattern, unit in UNIT_PATTERNS:
        if re.search(pattern, haystack):
            return unit
    return None


# ---------------------------------------------------------------------------
# Base unit definitions (template)
# ---------------------------------------------------------------------------

BASE_UNITS: list[dict] = [
    {"name": "/1", "label": {"one": "pourcent", "other": "pourcents"}, "ratio": True, "short_label": "%"},
    {"name": "year", "label": {"one": "année", "other": "années"}, "short_label": {"one": "an", "other": "ans"}},
    {"name": "month", "label": "mois"},
    {"name": "day", "label": {"one": "jour", "other": "jours"}},
    {"name": "trimestre", "label": {"one": "trimestre", "other": "trimestres"}},
    {"name": "index_point", "label": {"one": "point d'indice", "other": "points d'indice"}},
    {"name": "integer", "label": {"one": "entier", "other": "entiers"}},
    {"name": "enum", "label": {"one": "catégorie", "other": "catégories"}},
    {"name": "boolean", "label": {"one": "booléen", "other": "booléens"}},
]


def _build_currency_unit(name: str = "Euro", short: str = "€") -> dict:
    """Build a currency unit entry."""
    return {
        "name": "currency",
        "label": {"one": name, "other": f"{name}s"},
        "short_label": short,
    }


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def _find_package_dir(repo_path: Path) -> Path | None:
    for child in repo_path.iterdir():
        if child.is_dir() and child.name.startswith("openfisca_") and (child / "__init__.py").exists():
            return child
    return None


def scan_parameters(param_dir: Path) -> list[dict]:
    """Scan all YAML parameter files and return a list of file info dicts."""
    results = []
    for filepath in sorted(param_dir.rglob("*.yaml")):
        if filepath.name in ("index.yaml", "units.yaml"):
            continue
        try:
            data = yaml.safe_load(filepath.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue

        # Skip composite nodes (grade files with echelons, brackets, nested structures)
        if any(k in data for k in ("echelons", "brackets", "children")):
            continue
        # Skip nodes where all children are dicts (intermediate parameter nodes)
        non_meta_values = [
            v for k, v in data.items()
            if k not in ("description", "documentation", "metadata", "unit", "reference")
            and isinstance(v, dict)
        ]
        has_values = "values" in data or any(
            k for k in data if _looks_like_date(k)
        )
        if non_meta_values and not has_values:
            continue

        existing_unit = data.get("unit") or (data.get("metadata") or {}).get("unit")
        description = data.get("description", "")
        inferred = _infer_unit(filepath, description)

        results.append({
            "path": filepath,
            "relative": str(filepath.relative_to(param_dir.parent.parent)),
            "description": description,
            "existing_unit": existing_unit,
            "inferred_unit": inferred,
            "has_brackets": "brackets" in data,
        })
    return results


def build_units_yaml(scanned: list[dict], currency_name: str, currency_short: str) -> list[dict]:
    """Build the units.yaml content from scan results."""
    used_units: set[str] = set()
    for entry in scanned:
        if entry["existing_unit"]:
            used_units.add(entry["existing_unit"])
        if entry["inferred_unit"]:
            used_units.add(entry["inferred_unit"])

    units = [_build_currency_unit(currency_name, currency_short)]
    for base in BASE_UNITS:
        if base["name"] in used_units or base["name"] in {"/1", "year", "month", "currency"}:
            units.append(base)

    extra = used_units - {u["name"] for u in units}
    for name in sorted(extra):
        units.append({"name": name, "label": name})

    return units


def apply_units(scanned: list[dict], dry_run: bool = True) -> list[str]:
    """Add `unit:` field to parameter files that are missing it."""
    applied = []
    for entry in scanned:
        if entry["existing_unit"] or not entry["inferred_unit"]:
            continue
        if entry["has_brackets"]:
            continue

        filepath: Path = entry["path"]
        unit = entry["inferred_unit"]

        if dry_run:
            applied.append(f"  {entry['relative']}  →  unit: {unit}")
            continue

        text = filepath.read_text(encoding="utf-8")
        if "\nunit:" in text or text.startswith("unit:"):
            continue

        lines = text.splitlines(keepends=True)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("description"):
                insert_idx = i + 1
                break

        lines.insert(insert_idx, f"unit: {unit}\n")
        filepath.write_text("".join(lines), encoding="utf-8")
        applied.append(f"  ✓ {entry['relative']}  →  unit: {unit}")

    return applied


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: openfisca-ai init-units <package-path> [--apply] [--currency NAME SHORT]")
        print("\nExamples:")
        print("  openfisca-ai init-units . --currency Euro €")
        print("  openfisca-ai init-units . --currency Dinar DT --apply")
        sys.exit(1)

    repo_path = Path(args[0]).resolve()
    do_apply = "--apply" in args
    currency_name = "Euro"
    currency_short = "€"

    for i, arg in enumerate(args):
        if arg == "--currency" and i + 2 < len(args):
            currency_name = args[i + 1]
            currency_short = args[i + 2]

    pkg_dir = _find_package_dir(repo_path)
    if not pkg_dir:
        print(f"No openfisca_* package found in {repo_path}")
        sys.exit(1)

    param_dir = pkg_dir / "parameters"
    if not param_dir.is_dir():
        print(f"No parameters/ directory in {pkg_dir}")
        sys.exit(1)

    units_path = repo_path / "units.yaml"

    print(f"Package: {pkg_dir.name}")
    print(f"Parameters: {param_dir}")
    print()

    scanned = scan_parameters(param_dir)
    total = len(scanned)
    with_unit = sum(1 for e in scanned if e["existing_unit"])
    inferred = sum(1 for e in scanned if not e["existing_unit"] and e["inferred_unit"])
    unknown = sum(1 for e in scanned if not e["existing_unit"] and not e["inferred_unit"])

    print(f"Paramètres scannés : {total}")
    print(f"  Avec unité existante : {with_unit}")
    print(f"  Unité inférée : {inferred}")
    print(f"  Non déterminé : {unknown}")

    unit_counts = Counter()
    for e in scanned:
        u = e["existing_unit"] or e["inferred_unit"]
        if u:
            unit_counts[u] += 1

    print(f"\nUnités détectées :")
    for unit, count in unit_counts.most_common():
        print(f"  {unit:20s}  {count:4d} paramètres")

    # Generate units.yaml
    units_data = build_units_yaml(scanned, currency_name, currency_short)

    if units_path.exists():
        print(f"\nunits.yaml existe déjà : {units_path}")
        print(f"  Utilisez --force pour écraser (non implémenté, éditez manuellement)")
    else:
        units_text = yaml.dump(units_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
        if do_apply:
            units_path.write_text(units_text, encoding="utf-8")
            print(f"\n✓ units.yaml créé : {units_path}")
        else:
            print(f"\nunits.yaml qui serait généré :")
            print("---")
            print(units_text)
            print("---")

    # Apply units to parameter files
    print()
    changes = apply_units(scanned, dry_run=not do_apply)
    if changes:
        label = "Annotations appliquées" if do_apply else "Annotations proposées"
        print(f"{label} ({len(changes)}) :")
        for line in changes[:30]:
            print(line)
        if len(changes) > 30:
            print(f"  ... et {len(changes) - 30} de plus")
    else:
        print("Aucune annotation à appliquer.")

    if not do_apply and (changes or not units_path.exists()):
        print(f"\nPour appliquer : openfisca-ai init-units {repo_path} --apply")


if __name__ == "__main__":
    main()
