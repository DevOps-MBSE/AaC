"""Generated AaC Plugin hookimpls module for the gen-plugin plugin."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.package_resources import get_resource_file_contents, get_resource_file_path
from aac.io.parser import parse
from aac.plugins import hookimpl
from aac.plugins.gen_plugin.gen_plugin_impl import generate_plugin
from aac.plugins.plugin import Plugin

plugin_resource_file_args = (__package__, "gen_plugin.yaml")


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Returns the gen-plugin command type to the plugin infrastructure.

    Returns:
        A list of AacCommands
    """

    command_arguments = [
        AacCommandArgument(
            "architecture_file",
            "The yaml file containing the AaC DSL of the plugin architecture.",
        )
    ]

    plugin_commands = [
        AacCommand(
            "gen-plugin",
            "Generates an AaC plugin from an AaC model of the plugin",
            generate_plugin,
            command_arguments,
        )
    ]

    return plugin_commands


@hookimpl
def get_plugin_aac_definitions() -> str:
    """
    Return the plugin's AaC definitions.

    Returns:
         string representing yaml extensions and definitions defined by the plugin
    """

    return get_resource_file_contents(*plugin_resource_file_args)


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns the information about plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin_definitions = parse(
        get_plugin_aac_definitions(),
        get_resource_file_path(*plugin_resource_file_args)
    )

    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_commands(set(get_commands()))
    plugin.register_definitions(set(plugin_definitions))

    return plugin
