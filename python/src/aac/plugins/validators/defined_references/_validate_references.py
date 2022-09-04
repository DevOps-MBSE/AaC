import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


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
    findings = ValidatorFindings()

    def validate_dict(dict_to_validate: dict) -> None:

        reference_type = dict_to_validate.get("type")

        if reference_type:
            if language_context.is_primitive_type(reference_type) or language_context.is_definition_type(reference_type):
                logging.debug(f"Valid type reference. Type '{reference_type}' in content: {dict_to_validate}")
            else:
                undefined_reference_error_message = f"Undefined type '{reference_type}' referenced: {dict_to_validate}"
                findings.add_error_finding(definition_under_test, undefined_reference_error_message)
                logging.debug(undefined_reference_error_message)
        else:
            missing_field_in_dictionary = f"Missing field 'type' in validation content dictionary: {dict_to_validate}"
            findings.add_error_finding(definition_under_test, missing_field_in_dictionary)
            logging.debug(missing_field_in_dictionary)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult(definition_under_test, findings)
