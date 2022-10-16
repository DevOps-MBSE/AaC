import logging

from aac.lang.language_context import LanguageContext
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.definition import Definition
from aac.plugins.validators import ValidatorResult
from aac.plugins.validators._validator_findings import ValidatorFindings

PLUGIN_NAME = "Root key is defined"


def validate_root_keys(definition_under_test: Definition, target_schema_definition: Definition, language_context: LanguageContext, *validation_args) -> ValidatorResult:
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

    active_context_root_keys = get_active_context().get_root_keys()

    root_key = definition_under_test.get_root_key()

    if root_key not in active_context_root_keys:
        undefined_reference_error_message = f"Undefined root key '{root_key}' in definition '{definition_under_test.name}'. Valid root keys {active_context_root_keys}"
        findings.add_error_finding(definition_under_test, undefined_reference_error_message, PLUGIN_NAME, 0, 0, 0, 0)
        logging.debug(undefined_reference_error_message)

    return ValidatorResult([definition_under_test], findings)
