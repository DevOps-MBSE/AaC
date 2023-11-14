"""Module for the various date type contributions provided by this plugin."""

import logging

from datetime import datetime
from typing import Any, Optional

from aac.lang.constants import PRIMITIVE_TYPE_DATE
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.contributions.contribution_types.primitive_validation_contribution import PrimitiveValidationContribution
from aac.plugins.first_party.primitive_type_check.validators import DATE_VALIDATION_NAME
from aac.plugins.validators import FindingLocation, ValidatorFinding, FindingSeverity


def get_validator() -> PrimitiveValidationContribution:
    """Return the Primitive Validator for type 'date'."""
    return PrimitiveValidationContribution(DATE_VALIDATION_NAME, PRIMITIVE_TYPE_DATE, validate_date)


def validate_date(definition: Definition, value_to_validate: Any, _: LanguageContext) -> Optional[ValidatorFinding]:
    """
    Returns a validator finding if the value under test isn't a date.

    This validator returns an error if the date is not ISO 8601 compliant.

    Args:
        definition: The definition of the value to validate.
        value_to_validate: The value to validate.
        _ (LanguageContext): The current LanguageContext.

    Returns:
        A validator finding for the given value.
    """
    finding = None

    try:
        datetime.fromisoformat(str(value_to_validate))
    except ValueError as error:
        logging.debug(f"Failed to parse the date time string '{value_to_validate}' with error: '{error}'")
        finding_message = f"{value_to_validate} is not a valid ISO 8601 date for the {PRIMITIVE_TYPE_DATE} type."
        lexeme = definition.get_lexeme_with_value(value_to_validate)  # POPO Update
        finding_location = FindingLocation.from_lexeme(DATE_VALIDATION_NAME, lexeme)  # POPO Update
        finding = ValidatorFinding(definition, FindingSeverity.ERROR, finding_message, finding_location)

    return finding
