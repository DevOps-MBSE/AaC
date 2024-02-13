"""Provides classes for representing the results of executing a plugin."""
from enum import Enum, auto, unique
from attr import attrib, attrs, validators, Factory
from os import linesep
from typing import Optional

from aac.in_out.files.aac_file import AaCFile
from aac.context.source_location import SourceLocation


@unique
class ExecutionStatus(Enum):
    """An enumeration that represents status codes for AaC commands to return."""

    SUCCESS = 0
    CONSTRAINT_FAILURE = auto()
    CONSTRAINT_WARNING = auto()
    PARSER_FAILURE = auto()
    PLUGIN_FAILURE = auto()
    OPERATION_CANCELLED = auto()
    GENERAL_FAILURE = auto()


class MessageLevel(Enum):
    """An enumeration that represents the level of a message."""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@attrs(slots=True, auto_attribs=True)
class ExecutionMessage:
    """Provides a message for the user.

    Attributes:
        message (str): The textual content of the message.
        level (MessageLevel): value of MessageLevel.DEBUG, .INFO, .WARNING, or .ERROR
        source: (AaCFile): The file from whence the message came.
        location: (SourceLocation): The col, row info within the source file.
    """

    message: str = attrib(validator=validators.instance_of(str))
    level: MessageLevel = attrib(validator=validators.instance_of(MessageLevel))
    source: Optional[AaCFile] = attrib(
        validator=validators.optional(validators.instance_of(AaCFile))
    )
    location: Optional[SourceLocation] = attrib(
        validator=validators.optional(validators.instance_of(SourceLocation))
    )


@attrs(slots=True, auto_attribs=True)
class ExecutionResult:
    """Provides information regarding the results of the execution of a plugin.

    Attributes:
        plugin_name (str): The name of the plugin whose results are included.
        plugin_command_name (str): The name of the command which contributed to these results.
        status_code (ExecutionStatus): A status code for the plugin execution.
        messages (list[str]): A list of messages for the user.
    """

    plugin_name: str = attrib(validator=validators.instance_of(str))
    plugin_command_name: str = attrib(validator=validators.instance_of(str))
    status_code: ExecutionStatus = attrib(
        validator=validators.instance_of(ExecutionStatus)
    )
    messages: list[ExecutionMessage] = attrib(
        default=Factory(list), validator=validators.instance_of(list)
    )

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
                    result += f" (Ln {message.location.line}: Col {message.location.column}: Pos {message.location.position}: Spn {message.location.span})"
                result += linesep
        return result


@attrs(slots=True)
class ExecutionError(Exception):
    """A base class representing a plugin error condition.

    Attributes:
        message (str): a textual description of the reason for the exception.
    """

    message: str = attrib(validator=validators.instance_of(str))


@attrs(slots=True)
class OperationCancelled(Exception):
    """A base class representing an cancelled plugin operation condition.

    Attributes:
        message (str): a textual description of the reason for cancellation.
    """

    message: str = attrib(validator=validators.instance_of(str))
