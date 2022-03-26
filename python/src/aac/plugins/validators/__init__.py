"""A plugins sub-module specifically for 1st party validator plugins."""

from aac.parser import parse
from aac.parser.ParsedDefinition import ParsedDefinition
from aac.lang.definition_helpers import get_definitions_by_type


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
    validation_definitions = get_definitions_by_type(parsed_validator_definitions, "validation")

    if len(validation_definitions) != 1:
        raise RuntimeError(
            f"Expected one and only one validation defintion.\nValidation Definitions:\n{validation_definitions}"
        )

    return validation_definitions[0]
