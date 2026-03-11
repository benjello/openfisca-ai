#!/usr/bin/env python3
"""
Parameter Validation Tool - NO AI REQUIRED

Validates OpenFisca parameters against universal principles.
Usage: python validate_parameters.py /path/to/openfisca-country
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Set


class ParameterValidator:
    """Validate parameters without needing AI agents"""

    def __init__(self, package_path: Path):
        self.package_path = Path(package_path)
        self.errors = []
        self.warnings = []
        self.units_defined = set()
        self.units_used = set()

    def validate_all(self) -> Dict:
        """Run all validations"""
        print(f"🔍 Validating {self.package_path}...\n")

        # 1. Check units.yaml exists
        self.check_units_file()

        # 2. Validate all parameter files
        param_dir = self.package_path / "parameters"
        if param_dir.exists():
            self.validate_parameters(param_dir)

        # 3. Check units consistency
        self.check_units_consistency()

        return self.get_report()

    def check_units_file(self):
        """Principle 4: units.yaml must exist at package root"""
        units_file = self.package_path / "units.yaml"

        if not units_file.exists():
            self.errors.append({
                "type": "missing_units_file",
                "severity": "ERROR",
                "message": f"Missing {units_file} (required by Principle 4)",
                "file": str(units_file)
            })
            return

        # Load and parse units
        try:
            with open(units_file, 'r', encoding='utf-8') as f:
                units = yaml.safe_load(f)

            if not isinstance(units, list):
                self.errors.append({
                    "type": "invalid_units_format",
                    "severity": "ERROR",
                    "message": "units.yaml must be a YAML list",
                    "file": str(units_file)
                })
                return

            # Extract defined units
            for unit in units:
                if 'name' in unit:
                    self.units_defined.add(unit['name'])

            print(f"✅ Found units.yaml with {len(self.units_defined)} units defined")

        except Exception as e:
            self.errors.append({
                "type": "units_parse_error",
                "severity": "ERROR",
                "message": f"Failed to parse units.yaml: {e}",
                "file": str(units_file)
            })

    def validate_parameters(self, param_dir: Path):
        """Validate all parameter YAML files"""
        yaml_files = list(param_dir.rglob("*.yaml"))
        print(f"📋 Checking {len(yaml_files)} parameter files...\n")

        for yaml_file in yaml_files:
            # Skip units.yaml and index.yaml
            if yaml_file.name in ('units.yaml', 'index.yaml'):
                continue

            self.validate_parameter_file(yaml_file)

    def validate_parameter_file(self, filepath: Path):
        """Validate a single parameter file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)

            if not content:
                return

            # Check required metadata fields (Principle 4)
            self.check_metadata(filepath, content)

        except Exception as e:
            self.errors.append({
                "type": "parse_error",
                "severity": "ERROR",
                "message": f"Failed to parse: {e}",
                "file": str(filepath)
            })

    def check_metadata(self, filepath: Path, content: dict):
        """Check required metadata fields"""
        relative_path = filepath.relative_to(self.package_path)

        # Required fields per Principle 4
        required_fields = {
            'description': 'One clear sentence describing the parameter',
            'label': 'Short name for UI',
            'reference': 'Legal citation or URL with #page=XX',
            'unit': 'Unit of measure (required, see units.yaml)'
        }

        # Check metadata section
        metadata = content.get('metadata', {})

        for field, purpose in required_fields.items():
            # Check both root level and metadata section
            has_field = field in content or field in metadata

            if not has_field:
                self.errors.append({
                    "type": f"missing_{field}",
                    "severity": "ERROR",
                    "message": f"Missing '{field}' field ({purpose})",
                    "file": str(relative_path),
                    "principle": "Principle 4: Well-documented parameters"
                })

        # Track unit usage
        unit = content.get('unit') or metadata.get('unit')
        if unit:
            self.units_used.add(unit)

        # Check reference format (should have URLs with #page=XX for PDFs)
        self.check_reference_format(filepath, content)

    def check_reference_format(self, filepath: Path, content: dict):
        """Check that references include page numbers for PDFs"""
        reference = content.get('reference', [])

        if not reference:
            return

        if not isinstance(reference, list):
            reference = [reference]

        for ref in reference:
            if isinstance(ref, str):
                # Check if it's a PDF URL without #page=XX
                if '.pdf' in ref.lower() and '#page=' not in ref:
                    self.warnings.append({
                        "type": "missing_page_number",
                        "severity": "WARNING",
                        "message": f"PDF reference missing #page=XX: {ref}",
                        "file": str(filepath.relative_to(self.package_path)),
                        "principle": "Principle 3: Precise references"
                    })

    def check_units_consistency(self):
        """Check that all used units are defined in units.yaml"""
        if not self.units_defined:
            return  # Already reported missing units.yaml

        undefined_units = self.units_used - self.units_defined

        if undefined_units:
            for unit in undefined_units:
                self.errors.append({
                    "type": "undefined_unit",
                    "severity": "ERROR",
                    "message": f"Unit '{unit}' used but not defined in units.yaml",
                    "principle": "Principle 4: Well-documented parameters"
                })

        print(f"\n📊 Units: {len(self.units_used)} used, {len(self.units_defined)} defined")
        if undefined_units:
            print(f"❌ Undefined units: {', '.join(undefined_units)}")
        else:
            print("✅ All units properly defined")

    def get_report(self) -> Dict:
        """Generate validation report"""
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)

        if not self.errors and not self.warnings:
            print("\n✅ ALL CHECKS PASSED!\n")
            return {"valid": True, "errors": [], "warnings": []}

        if self.errors:
            print(f"\n❌ {len(self.errors)} ERRORS:\n")
            for error in self.errors:
                print(f"  [{error['severity']}] {error['file']}")
                print(f"    {error['message']}")
                if 'principle' in error:
                    print(f"    ({error['principle']})")
                print()

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} WARNINGS:\n")
            for warning in self.warnings:
                print(f"  [{warning['severity']}] {warning['file']}")
                print(f"    {warning['message']}")
                if 'principle' in warning:
                    print(f"    ({warning['principle']})")
                print()

        print("=" * 60)

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": {
                "units_defined": len(self.units_defined),
                "units_used": len(self.units_used),
                "undefined_units": list(self.units_used - self.units_defined)
            }
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_parameters.py /path/to/openfisca-country")
        print("\nExample:")
        print("  python validate_parameters.py /home/user/openfisca-tunisia")
        sys.exit(1)

    package_path = Path(sys.argv[1])

    if not package_path.exists():
        print(f"❌ Path not found: {package_path}")
        sys.exit(1)

    validator = ParameterValidator(package_path)
    report = validator.validate_all()

    # Exit with error code if validation failed
    sys.exit(0 if report['valid'] else 1)


if __name__ == "__main__":
    main()
