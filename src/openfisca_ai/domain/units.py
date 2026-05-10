"""Shared helpers for OpenFisca unit definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


USUAL_UNIT_DEFINITIONS: list[dict[str, Any]] = [
    {"name": "/1", "label": {"one": "pourcent", "other": "pourcents"}, "ratio": True, "short_label": "%"},
    {"name": "year", "label": {"one": "année", "other": "années"}, "short_label": {"one": "an", "other": "ans"}},
    {"name": "month", "label": "mois"},
    {"name": "day", "label": {"one": "jour", "other": "jours"}},
    {"name": "hour", "label": {"one": "heure", "other": "heures"}},
    {"name": "trimestre", "label": {"one": "trimestre", "other": "trimestres"}},
    {"name": "people", "label": {"one": "personne", "other": "personnes"}},
    {"name": "child", "label": {"one": "enfant", "other": "enfants"}},
    {"name": "integer", "label": {"one": "entier", "other": "entiers"}},
    {"name": "enum", "label": {"one": "catégorie", "other": "catégories"}},
    {"name": "boolean", "label": {"one": "booléen", "other": "booléens"}},
    {"name": "list", "label": {"one": "élément", "other": "éléments"}},
    {"name": "decile", "label": {"one": "décile", "other": "déciles"}},
    {"name": "index_point", "label": {"one": "point d'indice", "other": "points d'indice"}},
    {"name": "m3", "label": {"one": "mètre cube", "other": "mètres cubes"}, "short_label": "m³"},
    {"name": "kWh", "label": {"one": "kilowatt-heure", "other": "kilowatt-heures"}, "short_label": "kWh"},
    {"name": "m3/mois", "label": {"one": "mètre cube par mois", "other": "mètres cubes par mois"}, "short_label": "m³/mois"},
    {"name": "kWh/mois", "label": {"one": "kilowatt-heure par mois", "other": "kilowatt-heures par mois"}, "short_label": "kWh/mois"},
    {"name": "currency/kg", "label": {"one": "monnaie par kilogramme", "other": "monnaies par kilogramme"}, "short_label": "currency/kg"},
    {"name": "currency/l", "label": {"one": "monnaie par litre", "other": "monnaies par litre"}, "short_label": "currency/l"},
    {"name": "currency/m3", "label": {"one": "monnaie par mètre cube", "other": "monnaies par mètre cube"}, "short_label": "currency/m³"},
    {"name": "currency/unit", "label": {"one": "monnaie par unité", "other": "monnaies par unité"}, "short_label": "currency/unité"},
    {"name": "smig", "label": {"one": "SMIG", "other": "SMIG"}},
    {"name": "smic", "label": {"one": "SMIC", "other": "SMIC"}},
    {"name": "smic_horaire_brut", "label": {"one": "SMIC horaire brut", "other": "SMIC horaires bruts"}},
    {"name": "smic_mensuel_brut", "label": {"one": "SMIC mensuel brut", "other": "SMIC mensuels bruts"}},
]


def extract_unit_names(units: Any) -> set[str]:
    """Extract unit names from a parsed units.yaml payload."""
    if not isinstance(units, list):
        return set()
    return {
        unit["name"]
        for unit in units
        if isinstance(unit, dict) and "name" in unit
    }


def load_unit_names(units_file: Path) -> set[str]:
    """Load unit names from a units.yaml file."""
    with open(units_file, encoding="utf-8") as f:
        return extract_unit_names(yaml.safe_load(f))


def usual_unit_definitions(unit_names: set[str] | None = None) -> list[dict[str, Any]]:
    """Return generic unit definitions, optionally filtered by unit name.

    Country-specific units should not be added here. When a package already
    uses a non-generic unit, tools should preserve it as a minimal candidate in
    that package's generated units.yaml for human validation.
    """
    if unit_names is None:
        return [dict(unit) for unit in USUAL_UNIT_DEFINITIONS]
    return [dict(unit) for unit in USUAL_UNIT_DEFINITIONS if unit["name"] in unit_names]
