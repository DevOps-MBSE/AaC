"""The possible types of contributions that a plugin can make to AaC."""

from enum import Enum


class ContributionType(Enum):
    """The names of the contribution points that plugins can define."""

    COMMANDS = "commands"
    DEFINITIONS = "definitions"
    DEFINITION_VALIDATIONS = "validations"
    PRIMITIVE_VALIDATIONs = "primitive_validation"
