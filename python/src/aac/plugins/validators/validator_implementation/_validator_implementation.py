import logging

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.structure import get_substructures_by_type
from aac.plugins.plugin_manager import get_validator_plugins
from aac.plugins.validators import ValidatorResult, ValidatorPlugin


def validate_validator_implementations(definition_under_test: Definition, target_schema_definition: Definition, active_context: LanguageContext, **validation_kwargs) -> ValidatorResult:
    """
    Validates that the validation definition has a corresponding registered ValidatorPlugin.

    Args:
        definition_under_test (Definition): The definition that's being validate. (Root validation definitions)
        target_schema_definition (Definition): A definition with applicable validation. ("Validation" definition)
        active_context (LanguageContext): The active context.

    Returns:
        A ValidatorResult containing any applicable error messages.
    """
    error_messages = []

    def validate_dict(dict_to_validate: dict) -> list[str]:

        def get_validator_by_name(name: str, plugins: list[ValidatorPlugin]) -> ValidatorPlugin:
            return list(filter(lambda plugin: plugin.name == name, plugins))

        validator_implementations = get_validator_plugins()
        validation_name = dict_to_validate.get("name")

        validation_plugins = get_validator_by_name(validation_name, validator_implementations)

        if not validation_plugins:
            registered_plugin_names = [plugin.name for plugin in validator_implementations]
            registered_plugin_names = f"Validation '{validation_name}' did not have a corresponding implementation. Registered plugin names: {registered_plugin_names}"
            error_messages.append(registered_plugin_names)
            logging.debug(registered_plugin_names)
        elif validation_plugins and not len(validation_plugins) == 1:
            registered_plugin_names = [plugin.name for plugin in validator_implementations]
            registered_plugin_names = f"Validation '{validation_name}' returned multiple corresponding implementations. Matching plugins: {validation_plugins}"
            error_messages.append(registered_plugin_names)
            logging.debug(registered_plugin_names)

    dicts_to_test = get_substructures_by_type(definition_under_test, target_schema_definition, active_context)
    list(map(validate_dict, dicts_to_test))

    return ValidatorResult(error_messages, len(error_messages) == 0)
