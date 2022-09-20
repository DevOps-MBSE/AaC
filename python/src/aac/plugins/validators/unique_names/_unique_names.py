import logging

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.validators._validator_result import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Unique definition names"


def validate_unique_names(
    definition_under_test: Definition, target_schema_definition: Definition, language_context: LanguageContext, *validation_args
) -> ValidatorResult:
    """Search through the language context ensuring that all definition names are unique."""
    findings = ValidatorFindings()

    if definition_under_test.name in language_context.get_defined_types():
        duplicate_name_message = f"Definition name {definition_under_test.name} was duplicated in the language context."
        findings.add_error_finding(definition_under_test, duplicate_name_message, PLUGIN_NAME, 0, 0, 0, 0)
        logging.debug(duplicate_name_message)

    return ValidatorResult(definition_under_test, findings)
