"""Module for validating primitive string types."""

from typing import Any, Optional

from aac.lang.constants import PRIMITIVE_TYPE_STRING
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.contributions.contribution_types.primitive_validation_contribution import PrimitiveValidationContribution
from aac.plugins.first_party.primitive_type_check.validators import STRING_VALIDATION_NAME
from aac.plugins.validators import FindingLocation, FindingSeverity, ValidatorFinding


def get_validator() -> PrimitiveValidationContribution:
    """Return the Primitive Validator for 'int'."""
    return PrimitiveValidationContribution(STRING_VALIDATION_NAME, PRIMITIVE_TYPE_STRING, validate_string)


def validate_string(definition: Definition, value_to_validate: Any, _: LanguageContext) -> Optional[ValidatorFinding]:
    """
    Returns a Validation finding if the type isn't a valid string, otherwise None.

    This function is intended to be used in the Validation apparatus, and for this result
        to be collated with other findings into a larger ValidatorResult.

    Args:
        definition (Definition): The definition that the value belongs to.
        value_to_validate (Any): The value to test.
        _ (LanguageContext): The current LanguageContext.

    Returns:
        A ValidatorFinding if the value is not a string, or None.
    """
    if not isinstance(value_to_validate, str):
        finding_message = f"{value_to_validate} is not a valid {PRIMITIVE_TYPE_STRING} value."
        lexeme = definition.get_lexeme_with_value(value_to_validate) or definition.lexemes[0]    # POPO Update #
        finding_location = FindingLocation.from_lexeme(STRING_VALIDATION_NAME, lexeme)    # POPO Update #
        return ValidatorFinding(definition, FindingSeverity.ERROR, finding_message, finding_location)
