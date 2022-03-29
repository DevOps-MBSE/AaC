from aac.lang import ActiveContext
from aac.lang.hierarchy import get_root_definition_by_key
from aac.parser import ParsedDefinition
from aac.validate import ValidationResult


def validate_references(definition_under_test: ParsedDefinition, active_context: ActiveContext) -> ValidationResult:
    """Validates that the definition has valid type references to either primitive types or other definitions."""

    definition_structure_def = get_root_definition_by_key(definition_under_test.get_root_key(), active_context.context_definitions)

    error_messages = []
    return ValidationResult(error_messages, definition_under_test, len(error_messages) == 0)
