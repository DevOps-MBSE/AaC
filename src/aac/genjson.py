"""A plugin to print JSON schema of AaC model files."""
import json
import aac
from aac.AacCommand import AacCommand, AacCommandArgument


@aac.hookimpl
def get_commands() -> list[AacCommand]:
    """
    Provides the json command for integration into the CLI.

    Returns:
        list of AacCommands to register.
    """
    command_arguments = [
        AacCommandArgument(
            "architecture_files",
            "Space delimited list of one or more file paths to yaml file(s) containing models to parse and print as JSON.",
            number_of_arguments="+",
        )
    ]

    plugin_commands = [
        AacCommand("json", "Converts an AaC model to JSON", toJson, command_arguments)
    ]
    return plugin_commands


@aac.hookimpl
def get_base_model_extensions() -> None:
    """
    This plugin doesn't define any extensions, so returns None.
    """


def toJson(architecture_files: list[str]) -> None:
    """
    Prints the parsed_models from the parsed architecture_files values in JSON format.
    """

    for architecture_file in architecture_files:
        print(f"File: {architecture_file}")
        parsed_model = aac.parser.parse_file(architecture_file)
        _print_parsed_model(parsed_model)


def _print_parsed_model(parsed_model: dict[str, any]) -> None:
    print(json.dumps(parsed_model))
