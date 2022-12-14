"""AaC Plugin implementation module for the help-dump plugin."""

import json

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.serialization import AacCommandEncoder

plugin_name = "help-dump"


def help_dump() -> PluginExecutionResult:
    """
    Produce a formatted string containing all commands, their arguments, and each of their descriptions.

    Returns:
        help_output (str): The formatted string with all commands, etc.
    """

    def get_command_info():
        active_context = get_active_context()
        sorted_plugin_commands = sorted(active_context.get_plugin_commands(), key=lambda command: command.name)
        return json.dumps([encoder.default(command) for command in sorted_plugin_commands])

    encoder = AacCommandEncoder()
    with plugin_result(plugin_name, get_command_info) as result:
        return result
