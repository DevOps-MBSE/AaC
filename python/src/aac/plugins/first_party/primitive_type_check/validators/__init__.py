"""Module for the various type contributions provided by this plugin."""
import logging

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import (
    PRIMITIVE_TYPE_BOOL,
    PRIMITIVE_TYPE_DATE,
    PRIMITIVE_TYPE_FILE,
    PRIMITIVE_TYPE_INT,
    PRIMITIVE_TYPE_NUMBER,
    PRIMITIVE_TYPE_REFERENCE,
    PRIMITIVE_TYPE_STRING,
)
from aac.lang.definitions.lexeme import Lexeme
from aac.plugins.validators import FindingLocation
from aac.validate import ValidationError


def _create_validator_name(enum_type: str) -> str:
    return f"{enum_type}_enum_validator"


STRING_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_STRING)
INT_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_INT)
NUMBER_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_NUMBER)
BOOL_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_BOOL)
DATE_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_DATE)
FILE_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_FILE)
REFERENCE_VALIDATION_NAME = _create_validator_name(PRIMITIVE_TYPE_REFERENCE)


def get_finding_location(validation_name: str, lexeme: Lexeme) -> FindingLocation:
    """
    Convert a lexeme to a FindingLocation.

    Args:
        validation_name (str): The validation's name. Used to report which validation found the finding.
        lexeme (Lexeme): The lexeme used to populate the finding's line, position, and span

    Returns: A FindingLocation set to the same location and span as the lexeme.
    """
    active_context = get_active_context()
    source_file = active_context.get_file_in_context_by_uri(lexeme.source)

    if source_file is None:
        error_message = f"Attempted to create a type validation finding, but the source file '{lexeme.source}' isn't in the context."
        logging.error(error_message)
        raise ValidationError(error_message)
    else:
        lexeme_location = lexeme.location
        return FindingLocation(
            validation_name,
            source_file,
            lexeme_location.line,
            lexeme_location.column,
            lexeme_location.position,
            lexeme_location.span,
        )
