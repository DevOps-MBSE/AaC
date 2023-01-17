"""Module for the various number type contributions provided by this plugin."""
from typing import Any, Optional
import logging

from aac.lang.constants import PRIMITIVE_TYPE_NUMBER
from aac.lang.definitions.definition import Definition
from aac.plugins.contributions.contribution_types.primitive_validation_contribution import PrimitiveValidationContribution
from aac.plugins.first_party.primitive_type_check.validators import NUMBER_VALIDATION_NAME
from aac.plugins.first_party.primitive_type_check.validators.int_validator import validate_integer
from aac.plugins.validators import FindingLocation
from aac.plugins.validators._validator_finding import ValidatorFinding, FindingSeverity


def get_validator() -> PrimitiveValidationContribution:
    """Return the Primitive Validator for type 'number'."""
    return PrimitiveValidationContribution(NUMBER_VALIDATION_NAME, PRIMITIVE_TYPE_NUMBER, validate_number)


def validate_number(definition: Definition, value_to_validate: Any) -> Optional[ValidatorFinding]:
    """
    Returns a validator finding for the given value.

    This function is intended to be used in the Validation Apparatus,
    and for this result to be collated with other findings into a larger
    ValidatorResult.

    Args:
    - definition: The definition of the value to validate.
    - value_to_validate: The value to validate.

    Returns:
    - A validator finding for the given value.
    """

    is_invalid = not isinstance(value_to_validate, (int, float))
    finding = None
    if is_invalid:
        finding_message = f"{value_to_validate} is not a valid value for the number type {PRIMITIVE_TYPE_NUMBER}"
        lexeme = definition.get_lexeme_with_value(value_to_validate)
        finding_location = FindingLocation.from_lexeme(NUMBER_VALIDATION_NAME, lexeme)
        finding = ValidatorFinding(definition, FindingSeverity.ERROR, finding_message, finding_location)

    return finding
