"""The help-dump plugin module."""

from aac.cli.aac_command import AacCommand
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.first_party.help_dump.help_dump_impl import help_dump, plugin_name


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin.register_commands(_get_plugin_commands())
    return plugin


def _get_plugin_commands():
    plugin_commands = [
        AacCommand(
            "help-dump",
            "Produce a formatted string containing all commands, their arguments, and each of their descriptions.",
            help_dump,
        ),
    ]

    return plugin_commands
