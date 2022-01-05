"""Tools for handling plugin execution results consistently."""

from attr import attrib, attrs, validators
from enum import Enum, auto, unique


@unique
class PluginExecutionStatusCode(Enum):
    """An enumeration that represents status codes for plugins to return."""

    SUCCESS = auto()
    VALIDATION_FAILURE = auto()
    PLUGIN_FAILURE = auto()
    OPERATION_CANCELLED = auto()
    GENERAL_FAILURE = auto()


@attrs(slots=True, auto_attribs=True)
class PluginExecutionResult:
    """Provides information regarding the results of the execution of a plugin.

    Attributes:
        name (str): The name of the plugin whose results are included.
        status_code (PluginExecutionStatusCode): A status code for the plugin execution.
        messages (list[str]): A list of messages for the user.
    """

    name: str = attrib(validator=validators.instance_of(str))
    status_code: PluginExecutionStatusCode = attrib(
        validator=validators.instance_of(PluginExecutionStatusCode)
    )
    messages: list[str] = attrib(default=[], validator=validators.instance_of(list))

    def add_message(self, message: str) -> None:
        """Add a message to the list of messages."""
        self.messages.append(message)

    def set_messages(self, *messages) -> None:
        """Clear the current messages and set them to the passed in messages."""
        self.messages = list(messages)
