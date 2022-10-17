"""Module for the various type contributions provided by this plugin."""
from typing import Any, Optional

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
from aac.plugins.validators._validator_finding import ValidatorFinding


def _create_validator_name(enum_type: str) -> str:
    return f"{enum_type}_enum_validator"

INTEGER_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_INT)
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

    """
    is_invalid = False
    try:
        i = int(s)
    except ValueError as value_error:
        is_invalid = True
        pass
    except Exception as error:
        is_invalid = True
        pass

    # if is_invalid:




INTEGER_VALIDATOR = TypeValidationContribution(INTEGER_VALIDATION_NAME, PRIMITIVE_TYPE_INT, validate_integer)
