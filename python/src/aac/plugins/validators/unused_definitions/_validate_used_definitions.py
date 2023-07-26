import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.references import get_definition_type_references_from_list
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Validate definition references"
VALIDATION_NAME = "Definition references exist"


def validate_references(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the definition has valid definition references.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    def validate_used_definitions(definition_to_validate: Definition) -> None:
        for reference_to_validate in validation_args:
            if language_context.is_definition_type(reference_to_validate):
                logging.debug(f"Valid definition reference. Definition '{reference_to_validate}' in content: {definition_to_validate}")
            else:
                undefined_reference_error_message = f"Unused definition '{reference_to_validate}' referenced: {definition_to_validate}"
                reference_lexeme = definition_under_test.get_lexeme_with_value(reference_to_validate)
                logging.info(undefined_reference_error_message)

                if reference_lexeme:
                    findings.add_error_finding(
                        definition_under_test, undefined_reference_error_message, PLUGIN_NAME, reference_lexeme
                    )
                else:
                    logging.error(f"Definition '{reference_to_validate}' doesn't exist.")

    definitions_to_test = get_definition_type_references_from_list(definition_under_test, target_schema_definition)
    list(map(validate_used_definitions, definitions_to_test))

    return ValidatorResult([definition_under_test], findings)
