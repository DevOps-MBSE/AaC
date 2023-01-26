"""Module for validating primitive file types."""

from typing import Any, Optional

from aac.lang.constants import PRIMITIVE_TYPE_FILE
from aac.lang.definitions.definition import Definition
from aac.plugins.contributions.contribution_types.primitive_validation_contribution import PrimitiveValidationContribution
from aac.plugins.first_party.primitive_type_check.validators import FILE_VALIDATION_NAME
from aac.plugins.validators._validator_finding import ValidatorFinding


def get_validator() -> PrimitiveValidationContribution:
    """Return the Primitive Validator for 'file'."""
    return PrimitiveValidationContribution(FILE_VALIDATION_NAME, PRIMITIVE_TYPE_FILE, validate_file)


def validate_file(definition: Definition, value_to_validate: Any) -> Optional[ValidatorFinding]:
    """
    Returns a Validator finding if the type isn't a file that exists, otherwise None.

    This function is intended to be used in the Validation apparatus, and for this result
        to be called with other findings into a larger ValidatorResult.

    Args:
        definition (Definition): The definition that the value belongs to.
        value_to_validate (Any): The value to test.

    Returns:
        A ValidatorFinding if the value is not file path that exists on the file system, or None.
    """
    raise NotImplementedError("implement file primitive validator")
