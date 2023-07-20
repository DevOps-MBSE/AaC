"""Common utilities usable by all the plugins."""

import re

from functools import wraps
from typing import Callable, Dict, List, Optional

from aac.io.parser import parse
from aac.io.parser._parser_error import ParserError
from aac.lang.definitions.definition import Definition
from aac.package_resources import get_resource_file_contents, get_resource_file_path


REGISTERED_PLUGIN_COMMANDS: Dict[str, List[str]] = {}


def get_plugin_definitions_from_yaml(package, filename) -> list[Definition]:
    """Return the parsed plugin definitions from the plugin definition file."""
    try:
        yaml_definitions = parse(get_resource_file_contents(package, filename), get_resource_file_path(package, filename))
    except ParserError as error:
        raise ParserError(error.source, error.errors) from None
    else:
        return yaml_definitions


def register_plugin_command(plugin_name: str, command_name: Optional[str] = None) -> Callable:
    """
    Register a plugin command with the associated plugin.

    Args:
        plugin_name (str): The name of the plugin on which the command will be registered.
        command_name (str): The name of the command to be registered. (default: plugin_name)
    """
    global REGISTERED_PLUGIN_COMMANDS

    command_name, *_ = re.subn(r"[_ ]", "-", (command_name or plugin_name).lower())

    def wrapper(function: Callable):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if plugin_name in REGISTERED_PLUGIN_COMMANDS:
                REGISTERED_PLUGIN_COMMANDS[plugin_name].append(command_name)
            else:
                REGISTERED_PLUGIN_COMMANDS[plugin_name] = [command_name]

            return function(*args, **kwargs)

        return wrapped

    return wrapper
