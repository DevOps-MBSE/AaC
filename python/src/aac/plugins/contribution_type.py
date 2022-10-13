"""The possible types of contributions that a plugin can make to AaC."""

from enum import Enum


class ContributionType(Enum):
    """The names of the contribution points that plugins can define."""

    COMMANDS = "commands"
    VALIDATIONS = "validations"
    DEFINITIONS = "definitions"
    PRIMITIVE_VALIDATION = "primitive_validation"
