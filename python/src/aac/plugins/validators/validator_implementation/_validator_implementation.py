import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.lang.language_context import LanguageContext
from aac.plugins.validators import ValidatorFindings, ValidatorResult


PLUGIN_NAME = "Validation definition has an implementation"


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
        validator_implementations = language_context.get_definition_validations()
        validation_name = dict_to_validate.get("name")
        validation_plugins = [plugin for plugin in validator_implementations if plugin.name == validation_name]

        if not validation_plugins:
            registered_plugin_names = [plugin.name for plugin in validator_implementations]
            registered_plugin_names = f"Validation '{validation_name}' did not have a corresponding implementation. Registered plugin names: {registered_plugin_names}"
            validation_name_lexeme = definition_under_test.get_lexeme_with_value(validation_name)
            findings.add_error_finding(target_schema_definition, registered_plugin_names, PLUGIN_NAME, validation_name_lexeme)
            logging.debug(registered_plugin_names)
        elif validation_plugins and not len(validation_plugins) == 1:
            registered_plugin_names = [plugin.name for plugin in validator_implementations]
            registered_plugin_names = f"Validation '{validation_name}' returned multiple corresponding implementations. Matching plugins: {validation_plugins}"
            validation_name_lexeme = definition_under_test.get_lexeme_with_value(validation_name)
            findings.add_error_finding(target_schema_definition, registered_plugin_names, PLUGIN_NAME, validation_name_lexeme)
            logging.debug(registered_plugin_names)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, language_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult([definition_under_test], findings)
