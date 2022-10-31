"""The version plugin module."""

from aac.cli.aac_command import AacCommand
from aac.cli.builtin_commands.version.version_impl import version
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin

plugin_command = "version"


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_commands(_get_plugin_commands())
    return plugin


def _get_plugin_commands():
    plugin_commands = [
        AacCommand(
            plugin_command,
            "Print the AaC package version.",
            version,
        ),
    ]

    return plugin_commands
