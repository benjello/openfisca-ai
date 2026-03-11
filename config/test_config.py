#!/usr/bin/env python3
"""
Test configuration loading - Verify user.yaml setup

Usage: python config/test_config.py
"""

import sys
from pathlib import Path
import yaml


def test_config():
    """Test that configuration is properly set up"""
    print("=" * 70)
    print("Testing Configuration")
    print("=" * 70)
    print()

    config_dir = Path(__file__).parent
    user_config = config_dir / "user.yaml"
    template_config = config_dir / "user.yaml.template"

    # Check template exists
    if not template_config.exists():
        print("❌ Template not found: config/user.yaml.template")
        return False

    print(f"✅ Template exists: {template_config}")

    # Check user config exists
    if not user_config.exists():
        print(f"❌ User config not found: {user_config}")
        print()
        print("💡 Create it with:")
        print("   python config/setup.py")
        print("   OR")
        print("   cp config/user.yaml.template config/user.yaml")
        return False

    print(f"✅ User config exists: {user_config}")

    # Load and validate user config
    try:
        with open(user_config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if not config:
            print("❌ User config is empty")
            return False

        print()
        print("📋 Configuration loaded:")
        print(yaml.dump(config, default_flow_style=False))

        # Check required fields
        if 'countries' not in config:
            print("⚠️  No 'countries' field in config")
            return False

        # Resolve paths
        base_path = config.get('base_path', '')
        if base_path:
            print(f"📂 Base path: {base_path}")

        print()
        print("🗺️  Configured countries:")
        for country, settings in config['countries'].items():
            path_template = settings.get('path', '')
            # Simple variable substitution
            path = path_template.replace('${base_path}', base_path)
            path_obj = Path(path).expanduser()

            exists = path_obj.exists()
            status = "✅" if exists else "❌"

            print(f"   {status} {country}: {path}")
            if not exists:
                print(f"      ⚠️  Path does not exist")

        print()
        print("=" * 70)

        # Summary
        active = config.get('active_country', 'none')
        print(f"✅ Configuration valid!")
        print(f"   Active country: {active}")
        print(f"   Total countries: {len(config['countries'])}")
        print()

        return True

    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False


def main():
    success = test_config()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
