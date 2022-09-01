"""
A module for validator findings created when validator plugins want to provide information to a user
about a definition.

Validator findings include errors but need not be limited to errors, so this module also exports a
severity that informs how severe the finding is.
"""

from enum import Enum, auto


class Severity(Enum):
    """A severity for distinguishing between different kinds of validator findings."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
