"""
Housing allowance - Generic example for Countria.

Demonstrates:
- Parameter usage (no hardcoded values)
- Correct entity (Family)
- Vectorization (where)
- Precise references
"""

from openfisca_core.variables import Variable
from openfisca_core.periods import MONTH
from numpy import where


class housing_allowance(Variable):
    """Monthly housing allowance for low-income families."""

    value_type = float
    entity = Family  # Families receive the allowance
    definition_period = MONTH
    label = "Housing allowance"
    reference = "Social Benefits Act 2020, Section 12"

    def formula(family, period, parameters):
        """
        Calculate housing allowance.

        Eligibility: Family income < income ceiling
        Amount: Base amount (from parameters)
        """
        # Load parameters (NO hardcoded values!)
        ceiling = parameters(period).social_benefits.housing_allowance.income_ceiling
        base_amount = parameters(period).social_benefits.housing_allowance.base_amount

        # Calculate family income
        income = family("disposable_income", period)

        # Eligibility condition
        eligible = income < ceiling

        # Vectorized formula (where instead of if/else)
        return where(eligible, base_amount, 0)


class disposable_income(Variable):
    """Monthly disposable income of the family."""

    value_type = float
    entity = Family
    definition_period = MONTH
    label = "Disposable income"

    def formula(family, period):
        """Sum of all family members' income."""
        # Aggregate from Person to Family
        return family.sum(family.members("salary", period))


class salary(Variable):
    """Monthly salary (input variable)."""

    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Monthly salary"
