"""Module for the various number type contributions provided by this plugin."""

from typing import Any, Optional

from aac.lang.constants import PRIMITIVE_TYPE_NUMBER
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.contributions.contribution_types.primitive_validation_contribution import PrimitiveValidationContribution
from aac.plugins.first_party.primitive_type_check.validators import NUMBER_VALIDATION_NAME
from aac.plugins.validators import FindingLocation, ValidatorFinding, FindingSeverity


def get_validator() -> PrimitiveValidationContribution:
    """Return the Primitive Validator for type 'number'."""
    return PrimitiveValidationContribution(NUMBER_VALIDATION_NAME, PRIMITIVE_TYPE_NUMBER, validate_number)


def validate_number(definition: Definition, value_to_validate: Any, _: LanguageContext) -> Optional[ValidatorFinding]:
    """
    Returns a validator finding if the value under test isn't a number.

    Currently this validation is limited to testing if the python object is an int or float since
        validation is constrained to the YAML 1.1 spec as PyYAML has yet to implement the 1.2
        standard.

    Args:
        definition (Definition): The definition of the value to validate.
        value_to_validate (Any): The value to validate.
        _ (LanguageContext): The current LanguageContext.

    Returns:
        A validator finding for the given value.
    """
    finding = None
    if not isinstance(value_to_validate, (int, float)):
        finding_message = f"{value_to_validate} is not a valid value for the number type {PRIMITIVE_TYPE_NUMBER}."
        lexeme = definition.get_lexeme_with_value(value_to_validate)
        finding_location = FindingLocation.from_lexeme(NUMBER_VALIDATION_NAME, lexeme)
        finding = ValidatorFinding(definition, FindingSeverity.ERROR, finding_message, finding_location)

    return finding
