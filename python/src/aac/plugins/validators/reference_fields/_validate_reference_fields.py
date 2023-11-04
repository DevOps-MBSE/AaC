import logging

from aac.lang.constants import DEFINITION_FIELD_FIELDS, DEFINITION_FIELD_NAME, DEFINITION_FIELD_TYPE, PRIMITIVE_TYPE_REFERENCE
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.references import is_reference_format_valid
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Validate query reference format"
VALIDATION_NAME = "Reference format valid"


def validate_reference_fields(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the content of all specified reference fields is properly formatted.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.
        *validation_args: The names of the required fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    reference_field_names = validation_args
    schema_defined_fields_as_list = target_schema_definition.get_top_level_fields().get(DEFINITION_FIELD_FIELDS) or []  ### TODO: POPO update ###
    schema_defined_fields_as_dict = {field.get(DEFINITION_FIELD_NAME): field for field in schema_defined_fields_as_list} ### TODO: POPO update ###

    def validate_dict(dict_to_validate: dict) -> None:
        for reference_field_name in reference_field_names:
            field_value = dict_to_validate.get(reference_field_name)
            field_type = schema_defined_fields_as_dict.get(reference_field_name, {}).get(DEFINITION_FIELD_TYPE) ### TODO: POPO update ###

            # field type must be reference
            if field_type != PRIMITIVE_TYPE_REFERENCE:
                non_reference_field = f"Reference format validation cannot be performed on non-reference field '{reference_field_name}'.  Type is '{field_type}'"
                reference_field_name_lexeme = definition_under_test.get_lexeme_with_value(reference_field_name)
                findings.add_error_finding(
                    definition_under_test, non_reference_field, PLUGIN_NAME, reference_field_name_lexeme
                )
                logging.debug(non_reference_field)

            # field must not be empty
            elif field_value is None:
                missing_reference_field = f"Reference field '{reference_field_name}' value is missing"
                reference_field_name_lexeme = definition_under_test.get_lexeme_with_value(reference_field_name)
                findings.add_error_finding(
                    definition_under_test, missing_reference_field, PLUGIN_NAME, reference_field_name_lexeme
                )
                logging.debug(missing_reference_field)

            # field must be contain a parsable reference value
            elif not is_reference_format_valid(field_value):
                invalid_reference_format = f"Reference field '{reference_field_name}' is not properly formatted: {field_value}"
                reference_field_name_lexeme = definition_under_test.get_lexeme_with_value(reference_field_name)
                findings.add_error_finding(
                    definition_under_test, invalid_reference_format, PLUGIN_NAME, reference_field_name_lexeme
                )
                logging.debug(invalid_reference_format)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
