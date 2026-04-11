"""
Family benefits - Generic example for Countria.

Demonstrates:
- Max/min functions
- Indexed values
- Entity aggregation (Person → Family)
"""

from openfisca_core.variables import Variable
from openfisca_core.periods import MONTH
from numpy import minimum as min_


class number_of_children(Variable):
    """Number of children in the family (capped at 3)."""

    value_type = int
    entity = Family
    definition_period = MONTH
    label = "Number of children"

    def formula(family, period, parameters):
        """
        Count children, capped at maximum.

        According to Family Benefits Law 2018, Article 5:
        "Maximum 3 children counted for allowance calculation"
        """
        # Count all children
        is_child = family.members("is_child", period)
        total_children = family.sum(is_child)

        # Cap at maximum from parameters
        max_children = parameters(period).social_benefits.family_benefits.child_allowance.metadata.max_children

        # Return minimum (vectorized)
        return min_(total_children, max_children)


class child_allowance(Variable):
    """Monthly family benefits (child allowance)."""

    value_type = float
    entity = Family
    definition_period = MONTH
    label = "Child allowance"
    reference = "Family Benefits Law 2018, Article 5"

    def formula(family, period, parameters):
        """
        Calculate total child allowance.

        Amount = allowance_per_child × number_of_children (max 3)
        """
        # Load parameter
        allowance_per_child = parameters(period).social_benefits.family_benefits.child_allowance

        # Number of children (already capped)
        nb_children = family("number_of_children", period)

        # Total allowance
        return allowance_per_child * nb_children


class is_child(Variable):
    """Person is a child (age < 18)."""

    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Is child"

    def formula(person, period):
        """Child if age < 18."""
        age = person("age", period)
        return age < 18


class age(Variable):
    """Age of the person (input variable)."""

    value_type = int
    entity = Person
    definition_period = ETERNITY  # Age doesn't change within simulation
    label = "Age"
