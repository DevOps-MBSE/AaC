import logging

from aac.lang.context import ActiveContext
from aac.plugins.validators import ValidatorResult


def validate_references(validation_content: dict, active_context: ActiveContext) -> ValidatorResult:
    """Validates that the definition has valid type references to either primitive types or other definitions."""

    error_messages = []
    reference_type = validation_content.get("type")

    if reference_type:
        if not active_context.is_primitive_type(reference_type) and not active_context.is_definition_type(reference_type):
            undefined_reference_error_message = f"Undefined type '{reference_type}' referenced: {validation_content}"
            error_messages.append(undefined_reference_error_message)
            logging.debug(undefined_reference_error_message)
        else:
            logging.debug(f"Valid type reference. Type '{reference_type}' in content: {validation_content}")
    else:
        missing_field_in_dictionary = f"Missing field 'type' in validation content dictionary: {validation_content}"
        error_messages.append(missing_field_in_dictionary)
        logging.debug(missing_field_in_dictionary)

    return ValidatorResult(error_messages, len(error_messages) == 0)
