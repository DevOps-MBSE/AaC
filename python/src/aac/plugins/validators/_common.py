"""Module for common, shared functions specifically for the validator subclass of plugins."""

from aac.parser import parse
from aac.lang.definitions.definition import Definition
from aac.lang.definition_helpers import get_definitions_by_root_key
from aac.plugins import PluginError


def get_validation_definition_from_plugin_definitions(plugin_definitions_string: str) -> Definition:
    """
    Parses the validation definition sourced from a validator plugin's definitions.

    Args:
        plugin_definitions_string (str): The definitions as a yaml string

    Returns:
        The validation definition for the plugin.
    """
    # Temporary fix until plugins can provide better contextual information.
    parsed_validator_definitions = parse(plugin_definitions_string, "plugins.yaml")
    validation_definitions = get_definitions_by_root_key("validation", parsed_validator_definitions)

    if len(validation_definitions) != 1:
        raise PluginError(
            f"Expected one and only one validation definition.\nValidation Definitions:\n{validation_definitions}"
        )

    return validation_definitions[0]
