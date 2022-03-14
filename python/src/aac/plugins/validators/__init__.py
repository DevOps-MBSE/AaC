"""A plugins sub-module specifically for 1st party validator plugins."""

from aac import parser


def get_validation_definition_from_plugin_definitions(source_name: str, plugin_definitions_string: str) -> dict:
    """
    Parses the validation definition sourced from a validator plugin's definitions.

    Args:
        source_name (str): A name for the file source - necessary for error messages
        plugin_definitions_string (str): The definitions as a yaml string

    Returns:
        The validation definition for the plugin.
    """

    def is_validation_definition(definition):
        return "validation" in definition

    parsed_validator_definitions = parser.parse_str(source_name, plugin_definitions_string)
    validation_definitions = list(filter(is_validation_definition, parsed_validator_definitions.values()))

    if len(validation_definitions) != 1:
        raise RuntimeError(
            f"Expected one and only one validation defintion.\nValidation Definitions:\n{validation_definitions}"
        )

    return validation_definitions[0]
