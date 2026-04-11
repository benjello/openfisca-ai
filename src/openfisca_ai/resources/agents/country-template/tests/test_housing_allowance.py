"""
Tests for housing allowance - Generic example for Countria.

Demonstrates:
- Manual calculations in comments
- Edge cases (at threshold)
- Nominal cases
- References to legislation
"""

import pytest
from openfisca_core.simulation_builder import SimulationBuilder


def test_housing_allowance_eligible():
    """
    Test nominal case: eligible family.

    Manual calculation (Social Benefits Act 2020, Section 12, page 15):
    - Family income: 1200 CUR (< ceiling 1700)
    - Base amount: 220 CUR (2024 value)
    → Housing allowance = 220 CUR
    """
    tax_benefit_system = CountriaTaxBenefitSystem()  # Generic system
    builder = SimulationBuilder()
    builder.set_default_period("2024-01")

    simulation = builder.build_from_entities({
        "persons": {"parent": {}},
        "families": {"family": {"parents": ["parent"]}}
    })

    # Set input
    simulation.set_input("disposable_income", "2024-01", 1200)

    # Calculate
    allowance = simulation.calculate("housing_allowance", "2024-01")

    # Assert
    assert allowance == 220  # Base amount from parameters


def test_housing_allowance_not_eligible():
    """
    Test case: income above ceiling → not eligible.

    Manual calculation:
    - Family income: 1800 CUR (> ceiling 1700)
    → Housing allowance = 0 CUR
    """
    simulation = ...  # Setup as above
    simulation.set_input("disposable_income", "2024-01", 1800)

    allowance = simulation.calculate("housing_allowance", "2024-01")

    assert allowance == 0  # Not eligible


def test_housing_allowance_at_threshold():
    """
    Edge case: income exactly at ceiling.

    According to Social Benefits Act 2020, Section 12:
    "Families with income LESS THAN the ceiling" (strict inequality)

    - Family income: 1700 CUR (= ceiling)
    → Housing allowance = 0 CUR (not eligible)
    """
    simulation = ...
    simulation.set_input("disposable_income", "2024-01", 1700)

    allowance = simulation.calculate("housing_allowance", "2024-01")

    assert allowance == 0  # Exactly at threshold = not eligible


def test_housing_allowance_just_below_threshold():
    """
    Edge case: income just below ceiling.

    - Family income: 1699 CUR (< ceiling 1700)
    → Housing allowance = 220 CUR (eligible)
    """
    simulation = ...
    simulation.set_input("disposable_income", "2024-01", 1699)

    allowance = simulation.calculate("housing_allowance", "2024-01")

    assert allowance == 220  # Just below threshold = eligible


def test_housing_allowance_zero_income():
    """
    Edge case: zero income → always eligible.

    - Family income: 0 CUR
    → Housing allowance = 220 CUR
    """
    simulation = ...
    simulation.set_input("disposable_income", "2024-01", 0)

    allowance = simulation.calculate("housing_allowance", "2024-01")

    assert allowance == 220
