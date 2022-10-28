"""AaC Plugin implementation module for the help-dump plugin."""

import json


from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.plugins.plugin_manager import get_plugin_commands
from aac.cli.aac_command_encoder import AacCommandEncoder

plugin_name = "help-dump"


def help_dump() -> PluginExecutionResult:
    """
    Produce a formatted string containing all commands, their arguments, and each of their descriptions.

    Returns:
        help_output (str): The formatted string with all commands, etc.
    """

    def get_command_info():
        sorted_plugin_commands = sorted(get_plugin_commands(), key=lambda command: command.name)
        return json.dumps([encoder.default(command) for command in sorted_plugin_commands])

    encoder = AacCommandEncoder()
    with plugin_result(plugin_name, get_command_info) as result:
        return result
