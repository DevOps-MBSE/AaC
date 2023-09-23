from enum import Enum, auto, unique
from attr import attrib, attrs, validators, Factory
from os import linesep

@unique
class ExecutionStatus(Enum):
    """An enumeration that represents status codes for aac commands to return."""

    SUCCESS = 0
    VALIDATION_FAILURE = auto()
    PARSER_FAILURE = auto()
    PLUGIN_FAILURE = auto()
    OPERATION_CANCELLED = auto()
    GENERAL_FAILURE = auto()

@attrs(slots=True, auto_attribs=True)
class ExecutionResult:
    """Provides information regarding the results of the execution of a plugin.

    Attributes:
        name (str): The name of the plugin whose results are included.
        status_code (ExecutionStatus): A status code for the plugin execution.
        messages (list[str]): A list of messages for the user.
    """

    name: str = attrib(validator=validators.instance_of(str))
    status_code: ExecutionStatus = attrib(validator=validators.instance_of(ExecutionStatus))
    messages: list[str] = attrib(default=Factory(list), validator=validators.instance_of(list))

    def add_message(self, message: str) -> None:
        """Add a message to the list of messages."""
        self.messages.append(message)

    def add_messages(self, messages: list[str]) -> None:
        """Add messages to the list of messages."""
        self.messages.extend(messages)

    def is_success(self) -> bool:
        """Return True if the command succeeded; False, otherwise."""
        return self.status_code == ExecutionStatus.SUCCESS

    def get_messages_as_string(self) -> str:
        """Return the output messages as a combined string."""
        return linesep.join(self.messages)
    
@attrs(slots=True)
class ExecutionError(Exception):
    """A base class representing a plugin error condition."""

    message: str = attrib(validator=validators.instance_of(str))


@attrs(slots=True)
class OperationCancelled(Exception):
    """A base class representing an cancelled plugin operation condition."""

    message: str = attrib(validator=validators.instance_of(str))