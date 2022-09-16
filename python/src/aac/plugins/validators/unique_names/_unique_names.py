from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.plugins.validators._validator_result import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Unique definition names"


def validate_unique_names(definition_under_test: Definition, target_schema_definition: Definition, language_context: LanguageContext, *validation_args) -> ValidatorResult:
    findings = ValidatorFindings()
    return ValidatorResult(definition_under_test, findings)
