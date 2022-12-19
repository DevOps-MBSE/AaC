"""Module for the various type contributions provided by this plugin."""
from typing import Any, Optional

from aac.lang.constants import PRIMITIVE_TYPE_BOOL
from aac.lang.definitions.definition import Definition
from aac.plugins.contributions.contribution_types import PrimitiveValidationContribution
from aac.plugins.first_party.primitive_type_check.validators import BOOL_VALIDATION_NAME
from aac.plugins.validators._validator_finding import ValidatorFinding, FindingSeverity, FindingLocation


def get_validator() -> PrimitiveValidationContribution:
    """Return the Primitive Validator for 'boolean'."""
    return PrimitiveValidationContribution(BOOL_VALIDATION_NAME, PRIMITIVE_TYPE_BOOL, validate_bool)


def validate_bool(definition: Definition, value_to_validate: Any) -> Optional[ValidatorFinding]:
    """
    Returns a Validation finding if the type isn't valid, otherwise None.

    This function is intended to be used in the Validation apparatus, and for this result
    to be collated with other finding into a larger ValidatorResult.

    Arge:
        definition (Definition): The definition that the value belongs to.
        value_to_validate (Any): The value to be tested.

    Returns:
        A ValidatorFinding if the value is not a boolean or None.
    """

    is_invalid = not isinstance(value_to_validate, bool)
    finding = None
    if is_invalid:
        lexeme, *_ = [lexeme for lexeme in definition.lexemes if lexeme.value.lower() == str(value_to_validate.lower())]
        finding_message = f"{value_to_validate} is not a valid value for boolean type {PRIMITIVE_TYPE_BOOL}"
        finding_location = FindingLocation.from_lexeme(BOOL_VALIDATION_NAME, lexeme)
        finding = ValidatorFinding(definition, FindingSeverity.ERROR, finding_message, finding_location)

    return finding
