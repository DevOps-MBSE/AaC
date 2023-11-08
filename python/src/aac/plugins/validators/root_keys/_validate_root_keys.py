import logging

from aac.lang.definitions.definition import Definition  ### POPO update ###
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorResult
from aac.plugins.validators._validator_findings import ValidatorFindings


PLUGIN_NAME = "Validate root keys"
VALIDATION_NAME = "Root key is defined"


def validate_root_keys(
    definition_under_test: Definition,  ### POPO update ###
    target_schema_definition: Definition,   ### POPO update ###
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the definition root key is defined by the root definition.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    language_context_root_keys = language_context.get_root_keys()

    root_key = definition_under_test.get_root_key() ### POPO update ###

    if root_key not in language_context_root_keys:

        undefined_reference_error_message = f"Undefined root key '{root_key}' in definition '{definition_under_test.name}'. Valid root keys {language_context_root_keys}"   ### POPO update ###
        root_key_lexeme = definition_under_test.get_lexeme_with_value(root_key) ### POPO update ###
        findings.add_error_finding(definition_under_test, undefined_reference_error_message, PLUGIN_NAME, root_key_lexeme)  ### POPO update ###
        logging.debug(undefined_reference_error_message)

    return ValidatorResult([definition_under_test], findings)   ### POPO update ###
