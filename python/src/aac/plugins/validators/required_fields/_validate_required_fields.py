import logging
from typing import Any

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.definitions.type import is_array_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Required fields are present"


def validate_required_fields(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the definition has all required fields populated.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.
        *validation_args: The names of the required fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    required_field_names = validation_args
    schema_defined_fields_as_list = target_schema_definition.get_top_level_fields().get("fields") or []
    schema_defined_fields_as_dict = {field.get("name"): field for field in schema_defined_fields_as_list}

    def validate_dict(dict_to_validate: dict) -> None:
        for required_field_name in required_field_names:
            field_value = dict_to_validate.get(required_field_name)
            field_type = schema_defined_fields_as_dict.get(required_field_name, {}).get("type")

            if field_value is None:
                missing_required_field = f"Required field '{required_field_name}' missing from: {dict_to_validate}"
                required_field_lexeme = definition_under_test.get_lexeme_with_value(definition_under_test.get_root_key())
                findings.add_error_finding(definition_under_test, missing_required_field, PLUGIN_NAME, required_field_lexeme)
                logging.debug(missing_required_field)

            elif not _is_field_populated(field_type, field_value):
                unpopulated_required_field = f"Required field '{required_field_name}' is not populated in: {dict_to_validate}"
                required_field_lexeme = definition_under_test.get_lexeme_with_value(definition_under_test.get_root_key())
                findings.add_error_finding(
                    definition_under_test, unpopulated_required_field, PLUGIN_NAME, required_field_lexeme
                )
                logging.debug(unpopulated_required_field)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)


def _is_field_populated(field_type: str, field_value: Any) -> bool:
    """Return a boolean indicating is the field is considered 'populated'."""
    is_field_array_type = is_array_type(field_type)
    is_field_populated = False

    if is_field_array_type:
        is_field_populated = len(field_value) > 0
    elif type(field_value) is bool:
        is_field_populated = field_value is not None
    elif field_value:
        is_field_populated = True

    return is_field_populated
