"""AaC Plugin implementation module for the help-dump plugin."""

from iteration_utilities import flatten

from aac.plugins import plugin_manager
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.cli.aac_command import AacCommand

plugin_name = "help-dump"


def help_dump() -> PluginExecutionResult:
    """
    Produce a formatted string containing all commands, their arguments, and each of their descriptions.

    Returns:
        help_output (str): The formatted string with all commands, etc.
    """
    def get_command_info():
        return "\n".join([_format_command(command) for command in _get_all_commands()])

    with plugin_result(plugin_name, get_command_info) as result:
        return result


def _format_command(command: AacCommand) -> str:
    def format_argument(argument):
        return f"\n{argument.name}::{argument.description}"

    return (
        f"{command.name}::{command.description}::{len(command.arguments)}"
        + "".join(map(format_argument, command.arguments))
    )


def _get_all_commands() -> list[AacCommand]:
    all_plugins = plugin_manager.get_plugin_manager().get_plugins()
    return list(flatten([plugin.get_commands() for plugin in all_plugins if hasattr(plugin, "get_commands")]))
