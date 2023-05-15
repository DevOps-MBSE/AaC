import logging

from aac.lang.constants import DEFINITION_FIELD_NAME
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Validate implementations for validators"
VALIDATION_NAME = "Validation definition has an implementation"


def validate_validator_implementations(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the validation definition has a corresponding registered DefinitionValidationContribution.

    Args:
        definition_under_test (Definition): The definition that's being validated. (Root validation definitions)
        target_schema_definition (Definition): A definition with applicable validation. ("Validation" definition)
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    def validate_dict(dict_to_validate: dict) -> None:
        validation_name = dict_to_validate.get(DEFINITION_FIELD_NAME, "")
        active_validations = {
            validation.name: validation
            for validation in language_context.get_primitive_validations() + language_context.get_definition_validations()
        }

        if validation_name in active_validations and active_validations.get(validation_name).validation_function is None:
            no_implementation_error_message = f"Validation '{validation_name}' did not have a corresponding implementation."
            validation_name_lexeme = definition_under_test.get_lexeme_with_value(validation_name)
            findings.add_error_finding(
                target_schema_definition, no_implementation_error_message, PLUGIN_NAME, validation_name_lexeme
            )
            logging.debug(no_implementation_error_message)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
