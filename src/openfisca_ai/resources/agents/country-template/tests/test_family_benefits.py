"""
Tests for family benefits - Generic example for Countria.

Demonstrates:
- Integration tests (multiple children)
- Max children cap
- Manual calculations
"""

import pytest


def test_child_allowance_one_child():
    """
    Test: Family with 1 child.

    Manual calculation (Family Benefits Law 2018, Art. 5):
    - 1 child
    - Allowance per child: 65 CUR (2024 value)
    → Total = 65 CUR
    """
    simulation = ...  # Setup
    simulation = builder.build_from_entities({
        "persons": {
            "parent": {"age": 35},
            "child1": {"age": 5}
        },
        "families": {
            "family": {
                "parents": ["parent"],
                "children": ["child1"]
            }
        }
    })

    allowance = simulation.calculate("child_allowance", "2024-01")

    assert allowance == 65  # 1 child × 65


def test_child_allowance_three_children():
    """
    Test: Family with 3 children (maximum).

    Manual calculation:
    - 3 children (at maximum)
    - Allowance: 65 CUR per child
    → Total = 3 × 65 = 195 CUR
    """
    simulation = builder.build_from_entities({
        "persons": {
            "parent": {"age": 35},
            "child1": {"age": 5},
            "child2": {"age": 8},
            "child3": {"age": 12}
        },
        "families": {
            "family": {
                "parents": ["parent"],
                "children": ["child1", "child2", "child3"]
            }
        }
    })

    allowance = simulation.calculate("child_allowance", "2024-01")

    assert allowance == 195  # 3 × 65


def test_child_allowance_five_children_capped():
    """
    Test: Family with 5 children → capped at 3.

    According to Family Benefits Law 2018, Article 5:
    "Maximum 3 children counted for allowance"

    Manual calculation:
    - 5 children total
    - Maximum counted: 3 children
    - Allowance: 65 CUR per child
    → Total = 3 × 65 = 195 CUR (NOT 5 × 65)
    """
    simulation = builder.build_from_entities({
        "persons": {
            "parent": {"age": 40},
            "child1": {"age": 2},
            "child2": {"age": 5},
            "child3": {"age": 8},
            "child4": {"age": 12},
            "child5": {"age": 15}
        },
        "families": {
            "family": {
                "parents": ["parent"],
                "children": ["child1", "child2", "child3", "child4", "child5"]
            }
        }
    })

    # Verify number capped
    nb_children = simulation.calculate("number_of_children", "2024-01")
    assert nb_children == 3  # Capped at 3, not 5

    # Verify allowance
    allowance = simulation.calculate("child_allowance", "2024-01")
    assert allowance == 195  # 3 × 65 (not 5 × 65 = 325)


def test_child_allowance_no_children():
    """
    Edge case: Family with no children.

    → Total = 0 CUR
    """
    simulation = builder.build_from_entities({
        "persons": {"parent": {"age": 35}},
        "families": {"family": {"parents": ["parent"]}}
    })

    allowance = simulation.calculate("child_allowance", "2024-01")

    assert allowance == 0


def test_is_child_age_17():
    """
    Edge case: Person aged 17 → is child.

    Law: "child if age < 18"
    """
    simulation = ...
    simulation.set_input("age", "2024-01", 17)

    is_child_result = simulation.calculate("is_child", "2024-01")

    assert is_child_result == True  # 17 < 18


def test_is_child_age_18():
    """
    Edge case: Person aged 18 → NOT a child.

    Law: "child if age < 18" (strict inequality)
    """
    simulation = ...
    simulation.set_input("age", "2024-01", 18)

    is_child_result = simulation.calculate("is_child", "2024-01")

    assert is_child_result == False  # 18 >= 18
