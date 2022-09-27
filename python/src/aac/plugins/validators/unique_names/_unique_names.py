import logging
from os import linesep
from typing import Optional

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.language_context import LanguageContext
from aac.plugins.validators._validator_result import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Unique definition names"


def validate_unique_names(
    definition_under_test: Definition, target_schema_definition: Definition, language_context: LanguageContext, *validation_args
) -> ValidatorResult:
    """Search through the language context ensuring that all definition names are unique."""

    def is_duplicate_name(definition1: Definition, definition2: Definition) -> bool:
        lexeme1 = _get_lexeme_for_defined_name(definition1.name, definition1.lexemes)
        lexeme2 = _get_lexeme_for_defined_name(definition2.name, definition2.lexemes)
        return definition1.name == definition2.name and None not in [lexeme1, lexeme2] and lexeme1 != lexeme2

    findings = ValidatorFindings()

    definitions_with_target_name = [
        definition for definition in language_context.definitions if is_duplicate_name(definition_under_test, definition)
    ]

    if len(definitions_with_target_name) > 0:
        duplicate_name_message = _build_duplicate_name_message(definition_under_test, definitions_with_target_name)
        findings.add_error_finding(definition_under_test, duplicate_name_message, PLUGIN_NAME, 0, 0, 0, 0)
        logging.debug(duplicate_name_message)

    return ValidatorResult(definition_under_test, findings)


def _build_duplicate_name_message(definition: Definition, definitions: list[Definition]) -> str:
    message = [f"Definition '{definition.name}' is defined in:"]
    message += [f"  {definition.source.uri} at {_get_position(definition)}" for definition in definitions]
    return linesep.join(message)


def _get_position(definition: Definition) -> str:
    lexeme = _get_lexeme_for_defined_name(definition.name, definition.lexemes)
    return f"{lexeme.location.line + 1}:{lexeme.location.column}" if lexeme else "unknown location"


def _get_lexeme_for_defined_name(name: str, definition_lexemes: list[Lexeme]) -> Optional[Lexeme]:
    is_name_next = False
    for lexeme in definition_lexemes:
        if lexeme.value == "name":
            is_name_next = True
        elif lexeme.value == name and is_name_next:
            return lexeme
        else:
            is_name_next = False
