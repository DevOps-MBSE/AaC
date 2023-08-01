import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.references import get_definition_type_references_from_list
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Validate definition references"
VALIDATION_NAME = "Definition references exist"


def validate_used_definitions(
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

    if language_context.get_definition_by_name(target_schema_definition.name):
        logging.debug(f"Valid definition: {target_schema_definition.name}.")
        
        definitions_to_test = get_definition_type_references_from_list(target_schema_definition, definition_under_test)
        if len(definitions_to_test) > 0:
            logging.info(f"The definition {definition_under_test.name} references a valid definition {target_schema_definition.name}")
        else:
            logging.info(f"The definition {definition_under_test.name} does not reference another definition.")
    else:
        undefined_definition_error_message = f"Nonexistant definition: '{target_schema_definition.name}'."
        reference_lexeme = target_schema_definition.get_lexeme_with_value(target_schema_definition.name)
        logging.info(undefined_definition_error_message)

        if reference_lexeme:
            findings.add_error_finding(
                definition_under_test, undefined_definition_error_message, PLUGIN_NAME, reference_lexeme
            )

    return ValidatorResult([definition_under_test], findings)
