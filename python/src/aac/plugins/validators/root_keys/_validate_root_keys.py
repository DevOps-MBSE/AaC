import logging

from aac.lang.language_context import LanguageContext
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.validators import ValidatorResult


def validate_root_keys(definition_under_test: Definition, target_schema_definition: Definition, active_context: LanguageContext, *validation_args) -> ValidatorResult:
    """
    Validates that the definition root key is defined by the root definition.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        active_context (LanguageContext): The active context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    error_messages = []
    active_context_keys = get_active_context().get_root_keys()

    # We're expecting only full definition dicts -- so the root key is the first value
    root_key = definition_under_test.get_root_key()

    if root_key not in active_context_keys:
        undefined_reference_error_message = f"Undefined root key '{root_key}' in definition '{definition_under_test.name}'. Valid root keys {active_context_keys}"
        error_messages.append(undefined_reference_error_message)
        logging.debug(undefined_reference_error_message)

    return ValidatorResult(error_messages, len(error_messages) == 0)
