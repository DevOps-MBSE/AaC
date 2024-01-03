"""A simple data class to collect AaC command info from plugins."""

from typing import Any, Callable, Union

from attr import Factory, attrib, attrs, validators
from aac.context.definition import Definition


@attrs
class AacCommandArgument:
    """
    A class used to represent a command argument for an AaC command.

    Attributes:
        name: One or more strings with the name of the command argument.
        description: A string with the command argument description.
        data_type: The data type of the command argument.
        default: The default value for the current argument. (default: None)
    """

    name: Union[str, list[str]] = attrib(validator=validators.instance_of((list, str)))
    description: str = attrib(validator=validators.instance_of(str))
    data_type: str = attrib(validator=validators.instance_of(str))
    default: Any = attrib(default=None)


@attrs(hash=False)
class AacCommand:
    """
    A class used to represent a command in AaC.

    The command name is added to the argument parser with help set to the command description.
    The callback is invoked if the user specifies the command.

    Attributes:
        name: A string with the name of the command.
        description: A string with the command description -- will be used to populate the help command.
        callback: A function that's executed when the user runs the AaC command.
        arguments: A list of AacCommandArgument containing argument information about the command. (default: [])
    """

    name: str = attrib(validator=validators.instance_of(str))
    description: str = attrib(validator=validators.instance_of(str))
    callback: Callable[..., Any] = attrib(validator=validators.is_callable())
    arguments: list[AacCommandArgument] = attrib(
        default=Factory(list), validator=validators.instance_of(list)
    )

    def __hash__(self) -> int:
        """Return the hash of this AacCommand."""
        return hash(self.name)


@attrs(hash=False)
class PluginRunner:
    """
    A class used to manage the plugin execution invocation in AaC.

    Each plugin may define a set of commands and constraints.  The plugin runner contains the plugin definition
    and a mapping of command names to command callbacks and constraint names to constraint callbacks.

    Attributes:
        plugin_definition: The definition for the plugin.
        command_to_callback: Dictionary mapping command names to command callbacks.
        constraint_to_callback: Dictionary mapping constraint names to constraint callbacks.
    """

    plugin_definition: Definition = attrib(validator=validators.instance_of(Definition))
    command_to_callback: dict[str, Callable] = attrib(
        default={}, validator=validators.instance_of(dict)
    )
    constraint_to_callback: dict[str, Callable] = attrib(
        default={}, validator=validators.instance_of(dict)
    )

    # Add constraints here

    def add_command_callback(
        self, command_name: str, command_callback: Callable
    ) -> None:
        """Add a command callback to the plugin runner."""
        self.command_to_callback[command_name] = command_callback

    def add_constraint_callback(
        self, constraint_name: str, constraint_callback: Callable
    ) -> None:
        """Add a constraint callback to the plugin runner."""
        self.constraint_to_callback[constraint_name] = constraint_callback

    def get_constraint_callback(self, constraint_name: str) -> Callable:
        """Return the callback for the given constraint name."""
        return self.constraint_to_callback[constraint_name]

    def get_plugin_name(self) -> str:
        """Return the name of the plugin."""
        return self.plugin_definition.name
