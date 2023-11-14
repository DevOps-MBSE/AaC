"""Module for validating references to other AaC objects."""

from typing import Any, Optional

from aac.lang.constants import PRIMITIVE_TYPE_REFERENCE
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.contributions.contribution_types.primitive_validation_contribution import PrimitiveValidationContribution
from aac.plugins.first_party.primitive_type_check.validators import REFERENCE_VALIDATION_NAME
from aac.plugins.validators import FindingLocation, ValidatorFinding, FindingSeverity


def get_validator() -> PrimitiveValidationContribution:
    """Return the Primitive Validator for type 'reference'."""
    return PrimitiveValidationContribution(REFERENCE_VALIDATION_NAME, PRIMITIVE_TYPE_REFERENCE, validate_reference)


def validate_reference(
    definition: Definition, value_to_validate: Any, language_context: LanguageContext
) -> Optional[ValidatorFinding]:
    """
    Returns a validator finding if the value under test isn't a reference to an AaC definition.

    Args:
        definition (Definition): The definition of the value to validate.
        value_to_validate (Any): The value to validate.
        language_context (LanguageContext): The current LanguageContext.

    Returns:
        A validator finding for the given value.
    """
    finding = None
    if not language_context.get_definition_by_name(value_to_validate):
        finding_message = f"{value_to_validate} is not a valid reference to a definition."
        lexeme = definition.get_lexeme_with_value(value_to_validate)  # POPO Update
        finding_location = FindingLocation.from_lexeme(REFERENCE_VALIDATION_NAME, lexeme)  # POPO Update
        finding = ValidatorFinding(definition, FindingSeverity.ERROR, finding_message, finding_location)

    return finding
