"""
Income tax - Generic example for Countria.

Demonstrates:
- Progressive tax brackets
- Annual calculation
- TaxUnit entity
"""

from openfisca_core.variables import Variable
from openfisca_core.periods import YEAR


class income_tax(Variable):
    """Annual income tax (progressive brackets)."""

    value_type = float
    entity = TaxUnit  # Tax calculated at household tax unit level
    definition_period = YEAR
    label = "Income tax"
    reference = "Tax Code 2020, Schedule A"

    def formula(tax_unit, period, parameters):
        """
        Calculate income tax using progressive brackets.

        Tax Code 2020, Schedule A:
        - 0% on first 10,000 CUR
        - 10% on 10,000-25,000 CUR
        - 20% on 25,000-50,000 CUR
        - 30% above 50,000 CUR
        """
        # Taxable income
        taxable_income = tax_unit("taxable_income", period)

        # Load tax brackets from parameters
        brackets = parameters(period).taxation.income_tax.tax_brackets

        # Calculate tax using brackets (OpenFisca handles progression automatically)
        return brackets.calc(taxable_income)


class taxable_income(Variable):
    """Annual taxable income of the tax unit."""

    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Taxable income"

    def formula(tax_unit, period):
        """
        Sum of all tax unit members' annual salary.

        Note: In real implementation, would include deductions,
        exemptions, etc. Simplified here for demonstration.
        """
        # Aggregate annual salary from all members
        return tax_unit.sum(tax_unit.members("annual_salary", period))


class annual_salary(Variable):
    """Annual salary (12 × monthly salary)."""

    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Annual salary"

    def formula(person, period):
        """
        Sum monthly salaries over the year.

        Demonstrates period conversion: MONTH → YEAR
        """
        # OpenFisca automatically sums monthly values when requesting yearly
        return person("salary", period)


# Note: 'salary' is defined in housing_allowance.py (MONTH definition)
