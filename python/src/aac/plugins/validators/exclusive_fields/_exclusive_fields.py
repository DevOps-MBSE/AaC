import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Mutually exclusive fields"


def validate_exclusive_fields(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the none of the fields are simultaneously defined.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.
        *validation_args (list[str]): The list of exclusive fields.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    def validate_dict(dict_to_validate: dict) -> None:
        present_exclusive_fields = set(validation_args).intersection(set(dict_to_validate.keys()))

        if len(present_exclusive_fields) > 1:
            _, second, *_ = validation_args
            multiple_exclusive_fields = (
                f"Multiple exclusive fields are defined '{present_exclusive_fields}' in: {dict_to_validate}"
            )
            second_exclusive_field_lexeme = definition_under_test.get_lexeme_with_value(second)
            findings.add_error_finding(
                definition_under_test, multiple_exclusive_fields, PLUGIN_NAME, second_exclusive_field_lexeme
            )
            logging.debug(multiple_exclusive_fields)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
