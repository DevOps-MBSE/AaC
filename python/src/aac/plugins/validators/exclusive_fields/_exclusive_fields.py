
import logging

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorResult


def validate_exclusive_fields(definition_under_test: Definition, target_schema_definition: Definition, active_context: LanguageContext, *validation_args) -> ValidatorResult:
    """
    Validates that the none of the fields are simultaneously defined.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        active_context (LanguageContext): The active context.
        *validation_args (string): The list of exclusive fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    error_messages = []

    def validate_dict(dict_to_validate: dict) -> list[str]:
        present_exclusive_fields = set(validation_args).intersection(set(dict_to_validate.keys()))

        if len(present_exclusive_fields) > 1:
            multiple_exclusive_fields = f"Multiple exclusive fields are defined '{present_exclusive_fields}' in: {dict_to_validate}"
            error_messages.append(multiple_exclusive_fields)
            logging.debug(multiple_exclusive_fields)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, active_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult(error_messages, len(error_messages) == 0)
