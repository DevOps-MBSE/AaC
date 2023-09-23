"""The version plugin module."""

from aac.cli.aac_command import AacCommand
from aac.plugins.version.version_impl import plugin_name, version
from aac.cli import hookimpl
from aac.context.language_context import LanguageContext
from aac.lang.plugin import Plugin

@hookimpl
def register_plugin():
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin.commands(_get_plugin_commands())
    active_context = LanguageContext()
    active_context.register_instance(plugin)


def _get_plugin_commands():
    plugin_commands = [
        AacCommand(
            "version",
            "Print the AaC package version.",
            version,
        ),
    ]

    return plugin_commands
