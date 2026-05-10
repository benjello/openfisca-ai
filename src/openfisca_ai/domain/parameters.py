"""Shared helpers for OpenFisca parameter YAML files."""

from __future__ import annotations

from typing import Any


def get_metadata(content: dict[str, Any]) -> dict[str, Any]:
    """Return the metadata section when it is a mapping."""
    metadata = content.get("metadata", {})
    return metadata if isinstance(metadata, dict) else {}


def is_scale_parameter(content: dict[str, Any]) -> bool:
    """Return True when the parameter file defines brackets."""
    return isinstance(content, dict) and "brackets" in content


def get_reference_entries(content: dict[str, Any]) -> list[Any]:
    """Return normalized legal reference entries from root or metadata."""
    metadata = get_metadata(content)
    raw = content.get("reference") or metadata.get("reference")
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        entries: list[Any] = []
        for value in raw.values():
            if isinstance(value, list):
                entries.extend(value)
            elif isinstance(value, (dict, str)):
                entries.append(value)
        return entries
    return [raw]


def get_declared_units(content: dict[str, Any]) -> list[str]:
    """Return all unit names declared by a parameter file."""
    metadata = get_metadata(content)
    if is_scale_parameter(content):
        units = [
            metadata.get("threshold_unit"),
            metadata.get("rate_unit"),
            metadata.get("amount_unit"),
        ]
        return [unit for unit in units if unit]

    unit = content.get("unit") or metadata.get("unit")
    return [unit] if unit else []
