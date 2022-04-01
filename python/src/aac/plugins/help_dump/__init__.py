"""The help-dump plugin module."""

from aac.plugins import hookimpl
from aac.AacCommand import AacCommand
from aac.plugins.help_dump.help_dump_impl import help_dump


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Return a list of AacCommands provided by the plugin to register for use.

    This function is automatically generated. Do not edit.

    Returns:
        list of AacCommands
    """

    plugin_commands = [
        AacCommand(
            "help-dump",
            "Produce a formatted string containing all commands, their arguments, and each of their descriptions.",
            help_dump,
        ),
    ]

    return plugin_commands
