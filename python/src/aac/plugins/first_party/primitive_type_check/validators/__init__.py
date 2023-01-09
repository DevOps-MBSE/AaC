"""Module for the various type contributions provided by this plugin."""

from aac.lang.constants import (
    PRIMITIVE_TYPE_BOOL,
    PRIMITIVE_TYPE_DATE,
    PRIMITIVE_TYPE_FILE,
    PRIMITIVE_TYPE_INT,
    PRIMITIVE_TYPE_NUMBER,
    PRIMITIVE_TYPE_REFERENCE,
    PRIMITIVE_TYPE_STRING,
)


def _create_validator_name(enum_type: str) -> str:
    return f"{enum_type}_enum_validator"


plugin_name = "primitive-type-check"

STRING_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_STRING)
INT_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_INT)
NUMBER_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_NUMBER)
BOOL_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_BOOL)
DATE_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_DATE)
FILE_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_FILE)
REFERENCE_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_REFERENCE)
