#!/usr/bin/env python3
"""
Unit Validation Tool - Focus on units only

Validates that:
1. units.yaml exists
2. All parameters have a 'unit' field
3. All units used are defined in units.yaml

Usage: uv run python validate_units.py /path/to/openfisca-country
"""

import sys
from collections import defaultdict
from pathlib import Path

import yaml


class UnitsValidator:
    """Validate units only"""

    def __init__(self, package_path: Path):
        self.package_path = Path(package_path)
        self.units_defined = set()
        self.units_used = defaultdict(list)  # unit -> [files using it]
        self.files_without_unit = []
        self.files_with_units = set()
        self.parameter_files_count = 0

    def get_metadata(self, content: dict) -> dict:
        """Return the metadata section when present."""
        metadata = content.get("metadata", {})
        return metadata if isinstance(metadata, dict) else {}

    def get_units(self, content: dict) -> list[str]:
        """Return the declared units for a parameter file."""
        metadata = self.get_metadata(content)
        if "brackets" in content:
            units = [
                metadata.get("threshold_unit"),
                metadata.get("rate_unit"),
                metadata.get("amount_unit"),
            ]
            return [unit for unit in units if unit]

        unit = content.get("unit") or metadata.get("unit")
        return [unit] if unit else []

    def validate(self):
        """Run validation"""
        print(f"🔍 Validating units in {self.package_path}...\n")

        # 1. Check units.yaml
        if not self.check_units_file():
            return False

        # 2. Check all parameters
        param_dir = self.package_path / "parameters"
        if param_dir.exists():
            self.check_parameters(param_dir)

        # 3. Report
        return self.report()

    def check_units_file(self):
        """Check units.yaml exists and load units"""
        units_file = self.package_path / "units.yaml"

        if not units_file.exists():
            print(f"❌ Missing {units_file}")
            print("   All packages MUST have a units.yaml file at package root")
            return False

        try:
            with open(units_file, 'r', encoding='utf-8') as f:
                units = yaml.safe_load(f)

            if not isinstance(units, list):
                print(f"❌ units.yaml must be a YAML list")
                return False

            for unit in units:
                if 'name' in unit:
                    self.units_defined.add(unit['name'])

            print(f"✅ units.yaml found with {len(self.units_defined)} units defined:")
            for unit in sorted(self.units_defined):
                print(f"   - {unit}")
            print()

            return True

        except Exception as e:
            print(f"❌ Error reading units.yaml: {e}")
            return False

    def check_parameters(self, param_dir: Path):
        """Check all parameter files"""
        yaml_files = [f for f in param_dir.rglob("*.yaml")
                     if f.name not in ('units.yaml', 'index.yaml')]
        self.parameter_files_count = len(yaml_files)

        print(f"📋 Checking {len(yaml_files)} parameter files...\n")

        for yaml_file in yaml_files:
            self.check_parameter_file(yaml_file)

    def check_parameter_file(self, filepath: Path):
        """Check unit field in parameter file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)

            if not content:
                return

            relative_path = str(filepath.relative_to(self.package_path))
            units = self.get_units(content)

            if units:
                self.files_with_units.add(relative_path)
                for unit in units:
                    self.units_used[unit].append(relative_path)
            else:
                self.files_without_unit.append(relative_path)

        except Exception as e:
            print(f"⚠️  Error reading {filepath}: {e}")

    def report(self):
        """Generate report"""
        print("=" * 70)
        print("UNIT VALIDATION REPORT")
        print("=" * 70)
        print()

        # Summary
        total_files = self.parameter_files_count
        files_with_unit = len(self.files_with_units)

        print(f"📊 Summary:")
        print(f"   Total parameters: {total_files}")
        print(f"   With unit field: {files_with_unit} ({files_with_unit*100//total_files if total_files > 0 else 0}%)")
        print(f"   Missing unit: {len(self.files_without_unit)} ({len(self.files_without_unit)*100//total_files if total_files > 0 else 0}%)")
        print(f"   Units used: {len(self.units_used)}")
        print(f"   Units defined: {len(self.units_defined)}")
        print()

        # Check for undefined units
        undefined_units = set(self.units_used.keys()) - self.units_defined

        if undefined_units:
            print("❌ UNDEFINED UNITS:")
            for unit in sorted(undefined_units):
                print(f"\n   Unit '{unit}' not in units.yaml but used in:")
                for filepath in self.units_used[unit][:5]:  # Show first 5
                    print(f"     - {filepath}")
                if len(self.units_used[unit]) > 5:
                    print(f"     ... and {len(self.units_used[unit]) - 5} more files")
            print()
        else:
            print("✅ All used units are defined in units.yaml")
            print()

        # Files without unit
        if self.files_without_unit:
            print(f"❌ {len(self.files_without_unit)} FILES MISSING UNIT METADATA:")
            print()
            for filepath in self.files_without_unit[:20]:  # Show first 20
                print(f"   - {filepath}")
            if len(self.files_without_unit) > 20:
                print(f"   ... and {len(self.files_without_unit) - 20} more files")
                print()
                print(f"   Full list: {len(self.files_without_unit)} files need unit field")
            print()
            print("💡 Fix: Add 'unit: <unit_name>' to simple parameters")
            print("   For bracket parameters, use metadata.threshold_unit / rate_unit / amount_unit")
            print()
        else:
            print("✅ All parameters have unit metadata")
            print()

        # Units usage stats
        print("📈 Most used units:")
        sorted_units = sorted(self.units_used.items(), key=lambda x: len(x[1]), reverse=True)
        for unit, files in sorted_units[:10]:
            print(f"   {unit}: {len(files)} files")
        print()

        print("=" * 70)

        # Return success/failure
        has_errors = len(self.files_without_unit) > 0 or len(undefined_units) > 0
        return not has_errors


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python validate_units.py /path/to/openfisca-country")
        print("\nExample:")
        print("  uv run python validate_units.py /home/user/openfisca-tunisia")
        sys.exit(1)

    package_path = Path(sys.argv[1])

    if not package_path.exists():
        print(f"❌ Path not found: {package_path}")
        sys.exit(1)

    validator = UnitsValidator(package_path)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
