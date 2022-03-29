"""Module for common, shared functions specifically for the validator subclass of plugins."""

from aac.parser import parse, ParsedDefinition
from aac.lang.definition_helpers import get_definitions_by_root_key
from aac.plugins import PluginError


def get_validation_definition_from_plugin_definitions(plugin_definitions_string: str) -> ParsedDefinition:
    """
    Parses the validation definition sourced from a validator plugin's definitions.

    Args:
        source_name (str): A name for the file source - necessary for error messages
        plugin_definitions_string (str): The definitions as a yaml string

    Returns:
        The validation definition for the plugin.
    """
    parsed_validator_definitions = parse(plugin_definitions_string)
    validation_definitions = get_definitions_by_root_key("validation", parsed_validator_definitions)

    if len(validation_definitions) != 1:
        raise PluginError(
            f"Expected one and only one validation definition.\nValidation Definitions:\n{validation_definitions}"
        )

    return validation_definitions[0]
