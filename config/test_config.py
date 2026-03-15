#!/usr/bin/env python3
"""
Test configuration loading - Verify user.yaml setup

Usage: uv run python config/test_config.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from openfisca_ai.config_loader import (  # noqa: E402
    get_countries_dir,
    get_legislative_sources_root,
    get_reference_code_path,
    get_user_config_path,
    load_country_config,
)


def test_config():
    """Test that configuration is properly set up"""
    print("=" * 70)
    print("Testing Configuration")
    print("=" * 70)
    print()

    config_dir = Path(__file__).parent
    user_config = get_user_config_path()
    template_config = config_dir / "user.yaml.template"

    # Check template exists
    if not template_config.exists():
        print("❌ Template not found: config/user.yaml.template")
        return False

    print(f"✅ Template exists: {template_config}")

    # Check user config exists
    if not user_config.exists():
        print("❌ User config not found")
        print()
        print("💡 Create it with:")
        print("   uv run python config/setup.py")
        print("   OR")
        print("   cp config/user.yaml.template config/user.yaml")
        return False

    print(f"✅ User config exists: {user_config}")
    print()
    print("🗺️  Configured countries:")

    countries_dir = get_countries_dir()
    country_files = sorted(countries_dir.glob("*.yaml"))
    country_ids = [path.stem for path in country_files if not path.name.startswith("_")]

    if not country_ids:
        print("❌ No country configs found in config/countries/")
        return False

    ok = True
    for country_id in country_ids:
        config = load_country_config(country_id)
        if not config:
            print(f"   ❌ {country_id}: failed to load merged config")
            ok = False
            continue

        reference_path = get_reference_code_path(country_id)
        sources_root = get_legislative_sources_root(country_id)
        reference_status = "✅" if reference_path and reference_path.exists() else "⚠️"
        sources_status = "✅" if sources_root and sources_root.exists() else "⚠️"

        print(f"   {country_id}:")
        print(f"      {reference_status} existing_code.path: {reference_path or 'not configured'}")
        print(f"      {sources_status} legislative_sources.root: {sources_root or 'not configured'}")

        if reference_path is None and sources_root is None:
            ok = False

    print()
    print("=" * 70)
    print()
    print("✅ Configuration valid!" if ok else "⚠️  Configuration loaded with missing paths")
    print(f"   User config file: {user_config}")
    print(f"   Total countries: {len(country_ids)}")
    print()

    return ok


def main():
    success = test_config()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
