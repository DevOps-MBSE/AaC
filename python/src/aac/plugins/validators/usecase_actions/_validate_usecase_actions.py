import logging

from aac.lang.constants import (
    DEFINITION_FIELD_ACTION,
    DEFINITION_FIELD_BEHAVIOR,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_PARTICIPANTS,
    DEFINITION_FIELD_SOURCE,
    DEFINITION_FIELD_STEPS,
    DEFINITION_FIELD_TYPE,
    ROOT_KEY_USECASE,
)
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult

PLUGIN_NAME: str = "Validate usecase actions"
VALIDATION_NAME: str = "Usecase actions refer to defined model behaviors"


def validate_usecase_actions(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the usecase action field refers to a defined model behavior.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    if definition_under_test.get_root_key() == ROOT_KEY_USECASE:
        fields = definition_under_test.get_top_level_fields()  # POPO Update
        participants = fields.get(DEFINITION_FIELD_PARTICIPANTS, [])
        for step in fields.get(DEFINITION_FIELD_STEPS, []):
            action_name = step.get(DEFINITION_FIELD_ACTION)
            source_name = step.get(DEFINITION_FIELD_SOURCE)
            source_type, *_ = [
                participant.get(DEFINITION_FIELD_TYPE)
                for participant in participants
                if participant.get(DEFINITION_FIELD_NAME) == source_name
            ]
            source_fields = language_context.get_definition_by_name(source_type).get_top_level_fields()
            source_behaviors = [field.get(DEFINITION_FIELD_NAME) for field in source_fields.get(DEFINITION_FIELD_BEHAVIOR, [])]
            if action_name not in source_behaviors:
                invalid_action_reference_message = f"Action '{action_name}' does not refer to a behavior in '{source_name}'."
                logging.error(invalid_action_reference_message)
                findings.add_error_finding(
                    definition_under_test,
                    invalid_action_reference_message,
                    VALIDATION_NAME,
                    definition_under_test.get_lexeme_with_value(action_name),
                )

    else:
        logging.warn(f"Definition {definition_under_test.name} is not a {ROOT_KEY_USECASE}")

    return ValidatorResult([definition_under_test], findings)
