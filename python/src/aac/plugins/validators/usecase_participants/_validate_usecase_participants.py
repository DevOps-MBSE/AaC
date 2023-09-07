import logging

from aac.lang.constants import (
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_PARTICIPANTS,
    DEFINITION_FIELD_SOURCE,
    DEFINITION_FIELD_STEP,
    DEFINITION_FIELD_STEPS,
    DEFINITION_FIELD_TARGET,
    ROOT_KEY_USECASE,
)
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorResult, ValidatorFindings

PLUGIN_NAME: str = "Validate usecase participants"
VALIDATION_NAME: str = "Usecase sources and targets refer to defined participants"


def validate_usecase_participants(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that usecase source and target fields refer to defined participants.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """

    def get_invalid_reference_message(step_name: str, endpoint_type: str, endpoint: str):
        return (
            f"{endpoint_type.capitalize()} '{endpoint}' of step '{step_name}' does not refer to a participant of the usecase."
        )

    def validate_step_endpoint(step: dict[str, str], endpoint_type: str):
        step_name = step.get(DEFINITION_FIELD_STEP)
        endpoint = step.get(endpoint_type)
        if endpoint not in participants:
            invalid_endpoint_reference_message = get_invalid_reference_message(step_name, endpoint_type, endpoint)
            findings.add_error_finding(
                definition_under_test,
                invalid_endpoint_reference_message,
                VALIDATION_NAME,
                definition_under_test.get_lexeme_with_value(endpoint, prefix_values=[endpoint_type]),
            )
            logging.error(invalid_endpoint_reference_message)

    findings = ValidatorFindings()

    if definition_under_test.get_root_key() == ROOT_KEY_USECASE:
        fields = definition_under_test.get_top_level_fields()

        participants = [field.get(DEFINITION_FIELD_NAME) for field in fields.get(DEFINITION_FIELD_PARTICIPANTS, [])]
        for step in fields.get(DEFINITION_FIELD_STEPS, []):
            validate_step_endpoint(step, DEFINITION_FIELD_SOURCE)
            validate_step_endpoint(step, DEFINITION_FIELD_TARGET)

    else:
        logging.warn(f"Definition {definition_under_test.name} is not a {ROOT_KEY_USECASE}")

    return ValidatorResult([definition_under_test], findings)
