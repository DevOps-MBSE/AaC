"""The plugin-management plugin module."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.first_party.plugin_management.plugin_management_impl import (
    activate_plugin,
    deactivate_plugin,
    list_plugins,
    plugin_name,
)


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
    list_plugins_arguments = [
        AacCommandArgument(
            "--all",
            "Display a list of all the installed AaC plugins.",
            "bool",
            default=False,
        ),
        AacCommandArgument(
            "--active",
            "Display a list of all the active AaC plugins.",
            "bool",
            default=False,
        ),
        AacCommandArgument(
            "--inactive",
            "Display a list of all the inactive AaC plugins.",
            "bool",
            default=False,
        ),
    ]
    activate_plugin_arguments = [
        AacCommandArgument(
            "name",
            "The name of the plugin to be activated.",
            "str",
        ),
    ]
    deactivate_plugin_arguments = [
        AacCommandArgument(
            "name",
            "The name of the plugin to be deactivated.",
            "str",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "list-plugins",
            "Display a list of available plugins.",
            list_plugins,
            list_plugins_arguments,
        ),
        AacCommand(
            "activate-plugin",
            "Activate a plugin that's available and inactive on the system.",
            activate_plugin,
            activate_plugin_arguments,
        ),
        AacCommand(
            "deactivate-plugin",
            "Deactivate a plugin that's available and active on the system.",
            deactivate_plugin,
            deactivate_plugin_arguments,
        ),
    ]

    return plugin_commands
