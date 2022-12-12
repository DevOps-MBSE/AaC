import logging
from os import linesep
from aac.lang.constants import DEFINITION_FIELD_NAME

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.validators._validator_result import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Unique definition names"


def validate_unique_names(
    definition_under_test: Definition,
    target_schema_definition: Definition,
    language_context: LanguageContext,
    *validation_args,
) -> ValidatorResult:
    """Search through the language context ensuring that all definition names are unique."""

    def is_duplicate_name(definition1: Definition, definition2: Definition) -> bool:
        lexeme1 = definition1.get_lexeme_with_value(definition1.name)
        lexeme2 = definition2.get_lexeme_with_value(definition2.name)
        return definition1.name == definition2.name and None not in [lexeme1, lexeme2] and lexeme1 != lexeme2

    findings = ValidatorFindings()

    definitions_with_target_name = [
        definition for definition in language_context.definitions if is_duplicate_name(definition_under_test, definition)
    ]

    if len(definitions_with_target_name) > 0:
        duplicate_name_message = _build_duplicate_name_message(definition_under_test, definitions_with_target_name)
        definition_name_lexemes = [
            definition.get_lexeme_with_value(definition.name, prefix_values=[DEFINITION_FIELD_NAME])
            for definition in definitions_with_target_name
        ]
        for lexeme in definition_name_lexemes:
            findings.add_error_finding(definition_under_test, duplicate_name_message, PLUGIN_NAME, lexeme)
        logging.debug(duplicate_name_message)

    return ValidatorResult([definition_under_test], findings)


def _build_duplicate_name_message(definition: Definition, definitions: list[Definition]) -> str:
    line, column = _get_position(definition)
    message = [f"Definition '{definition.name}' is defined in:"]
    message += [f"  {definition.source.uri} at {line}:{column}" for definition in definitions]
    return linesep.join(message)


def _get_position(definition: Definition) -> tuple[int, int]:
    lexeme = definition.get_lexeme_with_value(definition.name)
    return lexeme.location.line + 1, lexeme.location.column
