import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.source_location import SourceLocation
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Type references exist"


def validate_references(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """
    Validates that the definition has valid type references to either primitive types or other definitions.

    Args:
        definition_under_test (Definition): The definition that's being validated.
        target_schema_definition (Definition): A definition with applicable validation.
        language_context (LanguageContext): The language context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    findings = ValidatorFindings()

    def validate_dict(dict_to_validate: dict) -> None:
        for reference_to_validate in validation_args:
            field_reference = dict_to_validate.get(reference_to_validate)
            if field_reference:
                if language_context.is_primitive_type(field_reference) or language_context.is_definition_type(field_reference):
                    logging.debug(f"Valid type reference. Type '{field_reference}' in content: {dict_to_validate}")
                else:
                    undefined_reference_error_message = f"Undefined type '{field_reference}' referenced: {dict_to_validate}"
                    reference_lexeme = definition_under_test.get_lexeme_with_value(field_reference)
                    logging.debug(undefined_reference_error_message)

                    if reference_lexeme:
                        findings.add_error_finding(
                            definition_under_test, undefined_reference_error_message, PLUGIN_NAME, reference_lexeme
                        )
                    else:
                        logging.debug(f"Value '{field_reference}' doesn't exist in definition. Likely an extension value.")

            else:
                missing_field_in_dictionary = f"Missing field 'type' in validation content dictionary: {dict_to_validate}"
                logging.debug(missing_field_in_dictionary)
                name_lexeme = definition_under_test.get_lexeme_with_value(definition_under_test.name)

                if not name_lexeme:
                    name_lexeme, *_ = definition_under_test.lexemes
                    name_lexeme = name_lexeme or Lexeme(SourceLocation(0, 0, 0, 0), definition_under_test.source.uri, definition_under_test.name)
                    logging.error(f"Definition '{definition_under_test.name}' is missing its name lexeme.")

                findings.add_error_finding(definition_under_test, missing_field_in_dictionary, PLUGIN_NAME, name_lexeme)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
