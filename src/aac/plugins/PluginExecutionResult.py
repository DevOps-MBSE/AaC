"""A class to provide context regarding the execution of a plugin command."""

from enum import Enum

from attr import attrib, attrs, validators


class PluginExecutionStatusCode(Enum):
    """An enumeration that represents status codes for plugins to return."""

    SUCCESS = 0
    VALIDATION_FAILURE = 1
    GENERAL_VAILURE = 256


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
