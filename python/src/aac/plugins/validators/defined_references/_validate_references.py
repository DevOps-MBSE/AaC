import logging

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorResult


def validate_references(definition_under_test: Definition, target_sub_definition: Definition, active_context: LanguageContext) -> ValidatorResult:
    """
    Validates that the definition has valid type references to either primitive types or other definitions.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_sub_definition (Definition): A definition with applicable validation.
        active_context (LanguageContext): The active context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    error_messages = []

    def validate_dict(dict_to_validate: dict) -> list[str]:

        reference_type = dict_to_validate.get("type")

        if reference_type:
            if active_context.is_primitive_type(reference_type) or active_context.is_definition_type(reference_type):
                logging.debug(f"Valid type reference. Type '{reference_type}' in content: {dict_to_validate}")
            else:
                undefined_reference_error_message = f"Undefined type '{reference_type}' referenced: {dict_to_validate}"
                error_messages.append(undefined_reference_error_message)
                logging.debug(undefined_reference_error_message)
        else:
            missing_field_in_dictionary = f"Missing field 'type' in validation content dictionary: {dict_to_validate}"
            error_messages.append(missing_field_in_dictionary)
            logging.debug(missing_field_in_dictionary)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_sub_definition, active_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult(error_messages, len(error_messages) == 0)
