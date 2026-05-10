"""Shared helpers for OpenFisca unit definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


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
