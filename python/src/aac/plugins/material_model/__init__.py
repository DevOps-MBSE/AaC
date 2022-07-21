"""The material-model plugin module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from aac.cli.aac_command import AacCommand
from aac.package_resources import get_resource_file_contents, get_resource_file_path
from aac.io.parser import parse
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin

plugin_resource_file_args = (__package__, "material_model.yaml")


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Return a list of AacCommands provided by the plugin to register for use.

    This function is automatically generated. Do not edit.

    Returns:
        list of AacCommands
    """

    plugin_commands = [
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
