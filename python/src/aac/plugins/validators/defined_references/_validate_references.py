import logging

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorResult


def validate_references(definition_under_test: Definition, target_schema_definition: Definition, language_context: LanguageContext, *validation_args) -> ValidatorResult:
    """
    Validates that the definition has valid type references to either primitive types or other definitions.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    error_messages = []
    validate_fields = validation_args
    fields_as_list = target_schema_definition.get_top_level_fields().get("fields") or []
    fields_as_dict = {field.get("name"): field for field in fields_as_list}

    def validate_dict(dict_to_validate: dict) -> list[str]:

        for validate_field in validate_fields:
            field_value = dict_to_validate.get(validate_field)
            field_type = fields_as_dict.get(validate_field, {}).get("type")

            # Verify that type is not blank
            if field_type is None:
                missing_type = f"Formatting error: '{validate_field}', is missing Type."
                error_messages.append(missing_type)
                logging.debug(missing_type)

            # Verify that the name is not blank
            elif field_value is None:
                missing_name = f"Formatting Error: '{validate_field}' is missing a value."
                error_messages.append(missing_name)
                logging.debug(missing_name)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult(error_messages, len(error_messages) == 0)
