"""The print-spec plugin module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from aac.cli.aac_command import AacCommand
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.print_spec.print_spec_impl import print_spec, print_active_context

plugin_resource_file_args = (__package__, "print-spec.yaml")


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
            "print-spec",
            "Print the AaC model describing core AaC data types and enumerations.",
            print_spec
        ),
        AacCommand(
            "print-active-context",
            "Print the AaC active language context including data types and enumerations added by plugins.",
            print_active_context
        ),
    ]

    return plugin_commands


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_commands(get_commands())

    return plugin
