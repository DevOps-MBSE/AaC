import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation
from aac.lang.definitions.structure import get_fields_by_enum_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Validate enum value is defined"
VALIDATION_NAME = "Enum value is defined"


def validate_enums(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the field's value is defined by the enum type of the field.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    def validate_dict(dict_to_validate: dict) -> None:
        # dict_to_validate is expected to be the enum field including the field name and value

        enum_value, *_ = dict_to_validate.values()
        defined_values = target_schema_definition.get_values()

        if enum_value not in defined_values:
            undefined_enum_value = f"Undefined enum value '{enum_value}' referenced in: {definition_under_test.name}"
            reference_lexeme = definition_under_test.get_lexeme_with_value(enum_value)
            logging.debug(undefined_enum_value)

            if reference_lexeme:
                findings.add_error_finding(
                    definition_under_test, undefined_enum_value, PLUGIN_NAME, reference_lexeme
                )
            else:
                logging.debug(f"Value '{enum_value}' doesn't exist in definition.")

    dicts_to_test = get_fields_by_enum_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
