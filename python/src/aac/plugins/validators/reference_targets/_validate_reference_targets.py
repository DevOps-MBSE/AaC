import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.references import get_reference_target_definitions, is_reference_format_valid
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import FindingLocation, ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Reference target valid"


def validate_reference_targets(
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
    schema_defined_fields_as_list = target_schema_definition.get_top_level_fields().get("fields") or []
    schema_defined_fields_as_dict = {field.get("name"): field for field in schema_defined_fields_as_list}

    def validate_dict(dict_to_validate: dict) -> None:
        for reference_field_name in reference_field_names:
            field_value = dict_to_validate.get(reference_field_name)
            field_type = schema_defined_fields_as_dict.get(reference_field_name, {}).get("type")

            # field type must be reference
            if field_type != "reference":
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
            elif not is_reference_format_valid(field_value)[0]:
                invalid_reference_format = f"Reference field '{reference_field_name}' is not properly formatted: {field_value} - {is_reference_format_valid(field_value)[1]}"
                reference_field_name_lexeme = definition_under_test.get_lexeme_with_value(reference_field_name)
                findings.add_error_finding(
                    definition_under_test, invalid_reference_format, PLUGIN_NAME, reference_field_name_lexeme
                )
                logging.debug(invalid_reference_format)

            # field must reference an existing target
            elif len(get_reference_target_definitions(field_value, language_context)) == 0:
                invalid_reference_target = (
                    f"Reference field '{reference_field_name}' does not have a defined target: {field_value}"
                )
                reference_field_name_lexeme = definition_under_test.get_lexeme_with_value(reference_field_name)
                findings.add_error_finding(
                    definition_under_test,
                    invalid_reference_target,
                    PLUGIN_NAME,
                    *FindingLocation.from_lexeme(PLUGIN_NAME, reference_field_name_lexeme).to_tuple(),
                )
                logging.debug(invalid_reference_target)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
