"""Module for common, shared functions specifically for the validator subclass of plugins."""

from typing import Callable
from aac.io.parser import parse

from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.definition import Definition
from aac.plugins import PluginError
from aac.plugins.contributions.contribution_types import DefinitionValidationContribution


def get_validation_definition_from_plugin_yaml(plugin_definitions_string: str) -> Definition:
    """
    Parses the validation definition sourced from a validator plugin's definitions.

    Args:
        plugin_definitions_string (str): The definitions as a yaml string

    Returns:
        The validation definition for the plugin.
    """
    return get_validation_definition_from_plugin_definitions(parse(plugin_definitions_string))


def get_validation_definition_from_plugin_definitions(validator_definitions: list[Definition]) -> Definition:
    """
    Find the Definition associated with the specific validator plugin.

    Args:
        validator_definitions (list[Definition]): The parsed list of Definitions from the validator plugin.

    Returns:
        The validation definition for the plugin.
    """
    validation_definitions = get_definitions_by_root_key("validation", validator_definitions)

    if len(validation_definitions) != 1:
        raise PluginError(
            f"Expected one and only one validation definition.\nValidation Definitions:\n{validation_definitions}"
        )

    return validation_definitions[0]


def get_plugin_validations_from_definitions(plugin_definitions: list[Definition], callback: Callable) -> list[DefinitionValidationContribution]:
    """
    Return the DefinitionValidationContribution based on the plugin definitions.

    Beware, plugins currently only support one validator per plugin.
    """
    validation_definition = get_validation_definition_from_plugin_definitions(plugin_definitions)
    return [DefinitionValidationContribution(validation_definition.name, validation_definition, callback)]
