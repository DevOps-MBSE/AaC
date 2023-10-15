from enum import Enum, auto, unique
from attr import attrib, attrs, validators, Factory
from os import linesep
from typing import Any, Optional

from aac.io.files.aac_file import AaCFile
from aac.context.source_location import SourceLocation

@unique
class ExecutionStatus(Enum):
    """An enumeration that represents status codes for aac commands to return."""

    SUCCESS = 0
    CONSTRAINT_FAILURE = auto()
    CONSTRAINT_WARNING = auto()
    PARSER_FAILURE = auto()
    PLUGIN_FAILURE = auto()
    OPERATION_CANCELLED = auto()
    GENERAL_FAILURE = auto()

@attrs(slots=True, auto_attribs=True)
class ExecutionMessage:
    """Provides a message for the user."""
    message: str = attrib(validator=validators.instance_of(str))
    source: Optional[AaCFile] = attrib(validator=validators.optional(validators.instance_of(AaCFile)))
    location: Optional[SourceLocation] = attrib(validator=validators.optional(validators.instance_of(SourceLocation)))

@attrs(slots=True, auto_attribs=True)
class ExecutionResult:
    """Provides information regarding the results of the execution of a plugin.

    Attributes:
        name (str): The name of the plugin whose results are included.
        status_code (ExecutionStatus): A status code for the plugin execution.
        messages (list[str]): A list of messages for the user.
    """

    plugin_name: str = attrib(validator=validators.instance_of(str))
    plugin_command_name: str = attrib(validator=validators.instance_of(str))
    status_code: ExecutionStatus = attrib(validator=validators.instance_of(ExecutionStatus))
    messages: list[ExecutionMessage] = attrib(default=Factory(list), validator=validators.instance_of(list))

    def add_message(self, message: ExecutionMessage) -> None:
        """Add a message to the list of messages."""
        self.messages.append(message)

    def add_messages(self, messages: list[ExecutionMessage]) -> None:
        """Add messages to the list of messages."""
        self.messages.extend(messages)

    def is_success(self) -> bool:
        """Return True if the command succeeded; False, otherwise."""
        return self.status_code == ExecutionStatus.SUCCESS

    def get_messages_as_string(self) -> str:
        """Return the output messages as a combined string."""
        result = ""
        for message in self.messages:
            result += message.message + linesep
            if message.source is not None:
                result += f"  Source: {message.source.uri}"
                if message.location is not None:
                    result += f" ({message.location.line}:{message.location.column}:{message.location.position}:{message.location.span})"
                result += linesep
        return result
    
    
@attrs(slots=True)
class ExecutionError(Exception):
    """A base class representing a plugin error condition."""

    message: str = attrib(validator=validators.instance_of(str))


@attrs(slots=True)
class LanguageError(Exception):
    """A base class representing a language error condition."""

    message: str = attrib(validator=validators.instance_of(str))


@attrs(slots=True)
class OperationCancelled(Exception):
    """A base class representing an cancelled plugin operation condition."""

    message: str = attrib(validator=validators.instance_of(str))