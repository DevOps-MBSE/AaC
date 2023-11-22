import logging
from aac.lang.constants import DEFINITION_FIELD_NAME

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.schema import get_definition_schema
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Validate undefined fields"
VALIDATION_NAME = "Disallow undefined fields"


def validate_undefined_fields(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the definition only has fields present that are defined in its defined schema.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.
        *validation_args: The names of the required fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    def validate_dict(dict_to_validate: dict) -> None:
        # Due to a bug in how global validations are currently being applied, we need to look up the schema rather
        #   than rely on the schema provided by the validation system.
        definition_schema = get_definition_schema(definition_under_test, language_context)  # POPO Update
        defined_field_names = [field.get(DEFINITION_FIELD_NAME) for field in definition_schema.get_fields()]

        # Iterate through the dict keys as those are the field names
        for field_name in dict_to_validate.keys():
            if field_name not in defined_field_names:
                undefined_field_message = f"Field '{field_name}' is not one of the fields defined in '{definition_schema.name}'."
                logging.error(undefined_field_message)
                findings.add_error_finding(
                    definition_under_test, undefined_field_message, VALIDATION_NAME, definition_under_test.get_lexeme_with_value(field_name)
                )

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)  # POPO Update
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
