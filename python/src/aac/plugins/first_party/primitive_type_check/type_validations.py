"""Module for the various type contributions provided by this plugin."""
from typing import Any, Optional
import logging

from aac.lang.constants import (
    PRIMITIVE_TYPE_STRING,
    PRIMITIVE_TYPE_INT,
    PRIMITIVE_TYPE_NUMBER,
    PRIMITIVE_TYPE_BOOL,
    PRIMITIVE_TYPE_DATE,
    PRIMITIVE_TYPE_FILE,
    PRIMITIVE_TYPE_REFERENCE,
)
from aac.lang.definitions.definition import Definition
from aac.plugins.contributions.contribution_types import TypeValidationContribution
from aac.plugins.validators._validator_finding import ValidatorFinding, FindingSeverity, FindingLocation


def _create_validator_name(enum_type: str) -> str:
    return f"{enum_type}_enum_validator"


STRING_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_STRING)
INT_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_INT)
NUMBER_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_NUMBER)
BOOL_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_BOOL)
DATE_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_DATE)
FILE_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_FILE)
REFERENCE_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_REFERENCE)


def validate_integer(definition: Definition, value_to_validate: Any) -> Optional[ValidatorFinding]:
    """
    Returns a Validation finding if the type isn't valid, otherwise None.

    This function is intended to be used in the Validation apparatus, and for this result
        to be collated with other findings into a larger ValidatorResult.

    Args:
        definition (Definition): The definition that the value belongs to.
        value_to_validate (Any): The value to test.

    Returns:
        A ValidatorFinding if the value is not an integer, or None.
    """
    is_invalid = False
    try:
        int(value_to_validate)
    except Exception as error:
        is_invalid = True
        logging.debug(f"{PRIMITIVE_TYPE_INT} validation failed for value {value_to_validate} with error:\n{error}")
        pass

    finding = None
    if is_invalid:
        finding_message = f"{value_to_validate} is not a valid value for the enum type {PRIMITIVE_TYPE_INT}"
        finding = ValidatorFinding(definition, FindingSeverity.ERROR, finding_message, FindingLocation())

    return finding


INTEGER_VALIDATOR = TypeValidationContribution(INT_VALIDATION_NAME, PRIMITIVE_TYPE_INT, validate_integer)
