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
        number_of_arguments: The number of entries that the argument can take. (default: 1)
        default: The default value for the current argument. (default: None)
    """

    name: Union[str, list[str]] = attrib(validator=validators.instance_of((list, str)))
    description: str = attrib(validator=validators.instance_of(str))
    data_type: str = attrib(validator=validators.instance_of(str))
    # number_of_arguments: int = attrib(default=1, validator=validators.instance_of(int))
    default: Any = attrib(default=None)


@attrs(hash=False)
class AacCommand:
    """
    A class used to represent a command in AaC.

    The command name is added to the argument parser with help set to the command description.
    The callback is invoked if the user specifies the command.

    Attributes:
        name: A string with the name of the command_description.
        description: A string with the command description -- will be used to build the help command.
        callback: A function that's executed when the user runs the AaC command.
        arguments: A list of AacCommandArgument containing argument information about the command. (default: [])
    """

    name: str = attrib(validator=validators.instance_of(str))
    description: str = attrib(validator=validators.instance_of(str))
    callback: Callable[..., Any] = attrib(validator=validators.is_callable())
    arguments: list[AacCommandArgument] = attrib(default=Factory(list), validator=validators.instance_of(list))

    def __hash__(self) -> int:
        """Return the hash of this AacCommand."""
        return hash(self.name)


@attrs(hash=False)
class PluginRunner:
    """
    A class used to represent a command in AaC.

    The command name is added to the argument parser with help set to the command description.
    The callback is invoked if the user specifies the command.

    Attributes:
        name: A string with the name of the command_description.
        description: A string with the command description -- will be used to build the help command.
        callback: A function that's executed when the user runs the AaC command.
        arguments: A list of AacCommandArgument containing argument information about the command. (default: [])
    """

    plugin_definition: Definition = attrib(validator=validators.instance_of(Definition))
    command_to_callback: dict[str, Callable] = attrib(default={}, validator=validators.instance_of(dict))
    constraint_to_callback: dict[str, Callable] = attrib(default={}, validator=validators.instance_of(dict))
    

    # Add constraints here

    def add_command_callback(self, command_name: str, command_callback: Callable) -> None:
        self.command_to_callback[command_name] = command_callback

    def add_constraint_callback(self, constraint_name: str, constraint_callback: Callable) -> None:
        self.constraint_to_callback[constraint_name] = constraint_callback

    def get_constraint_callback(self, constraint_name: str) -> Callable:
        return self.constraint_to_callback[constraint_name]

    def get_plugin_name(self) -> str:
        return self.plugin_definition.name

    