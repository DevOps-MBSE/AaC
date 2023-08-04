import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.references import get_definition_type_references_from_list
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Validate definition references"
VALIDATION_NAME = "Definition is referenced"


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
        target_schema_definition (Definition): The schema definition with the validation rules that trigger the validation.
        language_context (LanguageContext): A management and utility classfor the contextual AaC domain-specific language.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    # Check for additional references within the language context of the tested defintion
    referenced_definitions = get_definition_type_references_from_list(definition_under_test, language_context.definitions)

    # Get lexme for contributing to findings messages
    reference_lexeme = definition_under_test.get_lexeme_with_value(definition_under_test.name)

    if len(referenced_definitions) == 0:
        no_references_found_message = f"No references to '{definition_under_test.name}' in the language context."
        logging.info(no_references_found_message)
        if reference_lexeme:
            findings.add_info_finding(
                definition_under_test, no_references_found_message, PLUGIN_NAME, reference_lexeme
            )

    return ValidatorResult([definition_under_test], findings)
