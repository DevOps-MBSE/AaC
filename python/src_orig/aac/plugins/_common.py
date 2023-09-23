"""Common utilities usable by all the plugins."""

import logging as log

from functools import wraps
from typing import Callable, Dict, List

from aac.cli import AacCommand, AacCommandArgument
from aac.io.parser import ParserError, parse
from aac.lang.constants import (
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_DESCRIPTION,
    DEFINITION_FIELD_COMMANDS,
    DEFINITION_FIELD_HELP_TEXT,
    DEFINITION_FIELD_DISPLAY,
    DEFINITION_FIELD_TYPE,
    DEFINITION_FIELD_INPUT,
)
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.definitions.definition import Definition
from aac.package_resources import get_resource_file_contents, get_resource_file_path


REGISTERED_PLUGIN_COMMANDS: Dict[str, Dict[str, Callable]] = {}


def get_plugin_definitions_from_yaml(package, filename) -> list[Definition]:
    """Return the parsed plugin definitions from the plugin definition file."""
    try:
        yaml_definitions = parse(get_resource_file_contents(package, filename), get_resource_file_path(package, filename))
    except ParserError as error:
        raise ParserError(error.source, error.errors) from None
    else:
        return yaml_definitions


def register_plugin_command(plugin_name: str, command_name: str) -> Callable:
    """
    Register a plugin command with the associated plugin.

    Args:
        plugin_name (str): The name of the plugin on which the command will be registered.
        command_name (str): The name of the command to be registered.
    """
    global REGISTERED_PLUGIN_COMMANDS

    def wrapper(function: Callable):
        if plugin_name in REGISTERED_PLUGIN_COMMANDS:
            if command_name in REGISTERED_PLUGIN_COMMANDS[plugin_name]:
                log.warn(f"Overwriting implementation of command {command_name} in plugin {plugin_name}")

            REGISTERED_PLUGIN_COMMANDS[plugin_name].update({command_name: function})
        else:
            REGISTERED_PLUGIN_COMMANDS[plugin_name] = {command_name: function}

        @wraps(function)
        def wrapped(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapped

    return wrapper


def get_plugin_commands_from_definitions(plugin_name: str, plugin_definitions: List[Definition]) -> List[AacCommand]:
    """
    Return the AacCommands for the specified plugin.

    Args:
        plugin_name (str): The plugin name.
        plugin_definitions (List[Definition]): A collection of definitions contributed by the plugin.
    """

    from aac.plugins.first_party.gen_plugin import DEFINITION_FIELD_NUMBER_OF_ARGUMENTS, DEFINITION_FIELD_DEFAULT

    def get_command_name(structure):
        return structure.get(DEFINITION_FIELD_DISPLAY) or structure.get(DEFINITION_FIELD_NAME)

    definition = get_definition_by_name(plugin_name, plugin_definitions)
    command_structures = definition.get_top_level_fields().get(DEFINITION_FIELD_COMMANDS, []) if definition else []

    registered_commands = set(REGISTERED_PLUGIN_COMMANDS[plugin_name])
    modelled_commands = {get_command_name(cmd) for cmd in command_structures}
    undefined_commands = registered_commands.difference(modelled_commands)

    if undefined_commands:
        log.warn(f"There are commands that are not modelled in the '{plugin_name}' plugin definition: {undefined_commands}")

    plugin_commands = []
    for structure in command_structures:
        arguments = [
            AacCommandArgument(
                name=argument.get(DEFINITION_FIELD_NAME),
                description=argument.get(DEFINITION_FIELD_DESCRIPTION, ""),
                data_type=argument.get(DEFINITION_FIELD_TYPE),
                number_of_arguments=argument.get(DEFINITION_FIELD_NUMBER_OF_ARGUMENTS, 1),
                default=argument.get(DEFINITION_FIELD_DEFAULT),
            )
            for argument in structure.get(DEFINITION_FIELD_INPUT, [])
        ]

        command_name = get_command_name(structure)
        if command_name in REGISTERED_PLUGIN_COMMANDS[plugin_name]:
            plugin_commands.append(
                AacCommand(
                    command_name,
                    structure.get(DEFINITION_FIELD_HELP_TEXT, ""),
                    REGISTERED_PLUGIN_COMMANDS[plugin_name][command_name],
                    arguments,
                )
            )
        else:
            log.warn(f"The command {command_name} is not registered with the '{plugin_name}' plugin.")

    return plugin_commands
