"""The print-spec plugin module."""

from aac.cli.aac_command import AacCommand
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.first_party.print_spec.print_spec_impl import plugin_name, print_spec, print_active_context


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
            "print-spec",
            "Print the AaC model describing core AaC data types and enumerations.",
            print_spec,
        ),
        AacCommand(
            "print-active-context",
            "Print the AaC active language context including data types and enumerations added by plugins.",
            print_active_context,
        ),
    ]

    return plugin_commands
