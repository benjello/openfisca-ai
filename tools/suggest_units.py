#!/usr/bin/env python3
"""
Auto-suggest missing units based on filename patterns and context

Usage: python suggest_units.py /path/to/openfisca-country [--apply]
"""

import sys
import yaml
import re
from pathlib import Path
from collections import defaultdict


# Pattern-based unit suggestions
UNIT_PATTERNS = {
    # Age, durée, période
    r'age|duree|periode|stage|anciennete': 'year',

    # Taux, ratios, pourcentages
    r'taux|ratio|pourcent|coefficient|majoration|reduction|part': '/1',

    # Montants monétaires
    r'montant|plafond|plancher|ceiling|floor|seuil|threshold|pension|salaire|prime|allocation|prestation|revenu|income|benefice|indemnite|prix|cout|tarif': 'currency',

    # SMIG (Tunisia specific)
    r'smig|smic|minimum.*wage': 'smig',

    # Listes/énumérations
    r'liste|produits|categories': 'list',

    # Mois
    r'mois|mensuel': 'month',

    # Trimestre
    r'trimestre|trimestriel': 'trimestre',

    # Jours
    r'jour|day': 'day',
}


class UnitSuggester:
    """Suggest units for parameters missing them"""

    def __init__(self, package_path: Path):
        self.package_path = Path(package_path)
        self.units_defined = set()
        self.suggestions = []
        self.files_with_units = {}  # path -> unit (for pattern learning)

    def run(self, apply=False):
        """Run suggestion process"""
        print(f"🔍 Analyzing {self.package_path}...\n")

        # 1. Load units.yaml
        self.load_units()

        # 2. Scan all parameters
        param_dir = self.package_path / "parameters"
        if not param_dir.exists():
            print(f"❌ No parameters/ directory found")
            return

        self.scan_parameters(param_dir)

        # 3. Generate suggestions
        self.generate_report(apply)

    def load_units(self):
        """Load available units"""
        units_file = self.package_path / "units.yaml"

        if not units_file.exists():
            print(f"❌ Missing units.yaml")
            return

        with open(units_file, 'r', encoding='utf-8') as f:
            units = yaml.safe_load(f)

        for unit in units:
            if 'name' in unit:
                self.units_defined.add(unit['name'])

        print(f"✅ Loaded {len(self.units_defined)} available units\n")

    def scan_parameters(self, param_dir: Path):
        """Scan all parameter files"""
        yaml_files = [f for f in param_dir.rglob("*.yaml")
                     if f.name not in ('units.yaml', 'index.yaml')]

        print(f"📋 Scanning {len(yaml_files)} parameters...\n")

        for filepath in yaml_files:
            self.process_file(filepath)

    def process_file(self, filepath: Path):
        """Process a single parameter file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)

            if not content:
                return

            relative_path = filepath.relative_to(self.package_path)

            # Check if it's a scale/bracket parameter
            if 'brackets' in content:
                # Scale parameter - check for threshold_unit, rate_unit
                metadata = content.get('metadata', {})
                has_threshold = metadata.get('threshold_unit')
                has_rate = metadata.get('rate_unit')

                if has_threshold and has_rate:
                    # Already has units
                    self.files_with_units[str(relative_path)] = f"scale({has_threshold},{has_rate})"
                else:
                    # Suggest units for scale
                    suggestions = self.suggest_scale_units(filepath, content)
                    if suggestions:
                        self.suggestions.append({
                            'file': str(relative_path),
                            'filepath': filepath,
                            'suggested_unit': suggestions,
                            'confidence': 'HIGH' if 'bareme' in str(filepath).lower() else 'MEDIUM',
                            'content': content,
                            'is_scale': True
                        })
            else:
                # Simple parameter
                existing_unit = content.get('unit') or content.get('metadata', {}).get('unit')

                if existing_unit:
                    # Store for pattern learning
                    self.files_with_units[str(relative_path)] = existing_unit
                else:
                    # Suggest unit
                    suggested_unit = self.suggest_unit(filepath, content)
                    if suggested_unit:
                        self.suggestions.append({
                            'file': str(relative_path),
                            'filepath': filepath,
                            'suggested_unit': suggested_unit,
                            'confidence': self.calculate_confidence(filepath, suggested_unit),
                            'content': content,
                            'is_scale': False
                        })

        except Exception as e:
            print(f"⚠️  Error reading {filepath}: {e}")

    def suggest_scale_units(self, filepath: Path, content: dict) -> dict:
        """Suggest units for scale/bracket parameters"""
        path_str = str(filepath).lower()

        # Default suggestions for scales
        suggestions = {}

        # Threshold unit - usually currency, year, or trimestre
        if 'revenu' in path_str or 'income' in path_str or 'impot' in path_str or 'tax' in path_str:
            suggestions['threshold_unit'] = 'currency'
        elif 'age' in path_str or 'annuite' in path_str:
            suggestions['threshold_unit'] = 'trimestre' if 'trimestre' in self.units_defined else 'year'
        else:
            suggestions['threshold_unit'] = 'currency'  # Default

        # Rate unit - usually /1
        suggestions['rate_unit'] = '/1'

        return suggestions

    def suggest_unit(self, filepath: Path, content: dict) -> str:
        """Suggest unit based on patterns"""
        path_str = str(filepath).lower()

        # Try pattern matching on path
        for pattern, unit in UNIT_PATTERNS.items():
            if re.search(pattern, path_str):
                # Verify unit exists in units.yaml
                if unit in self.units_defined:
                    return unit
                # Map to available unit
                elif unit == 'currency' and 'currency' in self.units_defined:
                    return 'currency'

        # Check description for hints
        description = content.get('description', '').lower()
        for pattern, unit in UNIT_PATTERNS.items():
            if re.search(pattern, description):
                if unit in self.units_defined:
                    return unit

        # Default fallback
        if 'bareme' in path_str or 'scale' in path_str:
            return '/1'  # Barèmes are usually rates

        return None

    def calculate_confidence(self, filepath: Path, suggested_unit: str) -> str:
        """Calculate confidence level"""
        path_str = str(filepath).lower()

        # High confidence patterns
        high_confidence = [
            (r'age', 'year'),
            (r'taux', '/1'),
            (r'pension|salaire', 'currency'),
        ]

        for pattern, unit in high_confidence:
            if re.search(pattern, path_str) and suggested_unit == unit:
                return 'HIGH'

        return 'MEDIUM'

    def generate_report(self, apply=False):
        """Generate suggestion report"""
        if not self.suggestions:
            print("✅ All parameters have units!")
            return

        # Sort by confidence
        high = [s for s in self.suggestions if s['confidence'] == 'HIGH']
        medium = [s for s in self.suggestions if s['confidence'] == 'MEDIUM']

        print("=" * 70)
        print("UNIT SUGGESTIONS")
        print("=" * 70)
        print()

        print(f"📊 Summary:")
        print(f"   Total missing units: {len(self.suggestions)}")
        print(f"   High confidence: {len(high)}")
        print(f"   Medium confidence: {len(medium)}")
        print()

        if apply:
            print("🔧 APPLYING SUGGESTIONS...\n")
            applied = 0
            for suggestion in high:  # Only apply high confidence
                if self.apply_suggestion(suggestion):
                    applied += 1
            print(f"\n✅ Applied {applied}/{len(high)} high-confidence suggestions")
            print(f"⚠️  {len(medium)} medium-confidence suggestions need manual review\n")
        else:
            print("💡 HIGH CONFIDENCE (auto-apply safe):\n")
            for s in high[:20]:
                print(f"   {s['file']}")
                if s.get('is_scale'):
                    units = s['suggested_unit']
                    print(f"      → threshold_unit: {units.get('threshold_unit', 'N/A')}")
                    print(f"      → rate_unit: {units.get('rate_unit', 'N/A')}")
                else:
                    print(f"      → unit: {s['suggested_unit']}")
                print()

            if len(high) > 20:
                print(f"   ... and {len(high) - 20} more\n")

            if medium:
                print(f"\n⚠️  MEDIUM CONFIDENCE (manual review):\n")
                for s in medium[:10]:
                    print(f"   {s['file']}")
                    print(f"      → unit: {s['suggested_unit']} (verify manually)")
                    print()

                if len(medium) > 10:
                    print(f"   ... and {len(medium) - 10} more\n")

        print("=" * 70)
        print()

        if not apply:
            print("💡 To apply high-confidence suggestions automatically:")
            print("   python suggest_units.py <path> --apply")
            print()

    def apply_suggestion(self, suggestion: dict) -> bool:
        """Apply a unit suggestion to a file"""
        try:
            filepath = suggestion['filepath']
            unit = suggestion['suggested_unit']

            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find where to insert unit
            # Strategy: insert after description or at beginning of metadata
            new_lines = []
            inserted = False

            for i, line in enumerate(lines):
                new_lines.append(line)

                # Insert after description line
                if not inserted and re.match(r'^description:', line):
                    # Get indentation
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent + f'unit: {unit}\n')
                    inserted = True

            # If not inserted, try adding to metadata section
            if not inserted:
                for i, line in enumerate(new_lines):
                    if re.match(r'^metadata:', line):
                        indent = len(line) - len(line.lstrip())
                        # Insert unit as first item in metadata
                        new_lines.insert(i + 1, ' ' * (indent + 2) + f'unit: {unit}\n')
                        inserted = True
                        break

            # If still not inserted, add at top level before values
            if not inserted:
                for i, line in enumerate(new_lines):
                    if re.match(r'^values:', line):
                        indent = len(line) - len(line.lstrip())
                        new_lines.insert(i, ' ' * indent + f'unit: {unit}\n')
                        inserted = True
                        break

            if inserted:
                # Write back
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)

                print(f"✅ {suggestion['file']} → unit: {unit}")
                return True
            else:
                print(f"⚠️  Could not insert unit in {suggestion['file']}")
                return False

        except Exception as e:
            print(f"❌ Error applying suggestion to {suggestion['file']}: {e}")
            return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python suggest_units.py /path/to/openfisca-country [--apply]")
        print("\nExamples:")
        print("  python suggest_units.py /home/user/openfisca-tunisia")
        print("  python suggest_units.py /home/user/openfisca-tunisia --apply")
        sys.exit(1)

    package_path = Path(sys.argv[1])
    apply = '--apply' in sys.argv

    if not package_path.exists():
        print(f"❌ Path not found: {package_path}")
        sys.exit(1)

    suggester = UnitSuggester(package_path)
    suggester.run(apply=apply)


if __name__ == "__main__":
    main()
