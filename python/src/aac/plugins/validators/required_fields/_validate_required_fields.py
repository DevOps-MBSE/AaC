import logging

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorResult


def validate_required_fields(definition_under_test: Definition, target_schema_definition: Definition, language_context: LanguageContext, *validation_args) -> ValidatorResult:
    """
    Validates that the definition has all required fields populated.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    error_messages = []

    def validate_dict(dict_to_validate: dict) -> list[str]:

        required_fields = target_schema_definition.get_required()

        for required_field in required_fields:

            if required_field not in dict_to_validate:
                missing_required_field = f"Required field '{required_field}' missing from: {dict_to_validate}"
                error_messages.append(missing_required_field)
                logging.debug(missing_required_field)
            # Rely on python truthy to test for empty arrays, strings, or undefined fields.
            elif not dict_to_validate.get(required_field):
                unpopulated_required_field = f"Required field '{required_field}' is not populated in: {dict_to_validate}"
                error_messages.append(unpopulated_required_field)
                logging.debug(unpopulated_required_field)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult(error_messages, len(error_messages) == 0)
