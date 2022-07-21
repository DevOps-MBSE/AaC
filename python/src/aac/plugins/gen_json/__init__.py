"""Generated AaC Plugin hookimpls module for the aac-gen-json plugin."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.io.parser import parse
from aac.package_resources import get_resource_file_contents, get_resource_file_path
from aac.plugins import hookimpl
from aac.plugins.gen_json.gen_json_impl import print_json
from aac.plugins.plugin import Plugin


plugin_resource_file_args = (__package__, "gen_json.yaml")


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Provides the json command for integration into the CLI.

    Returns:
        list of AacCommands to register.
    """
    command_arguments = [
        AacCommandArgument(
            "architecture_files",
            "Space delimited list of one or more file paths to yaml file(s) containing models to parse and print as JSON.",
            number_of_arguments="+",
        ),
        AacCommandArgument(
            "--output_directory",
            "Directory in which JSON files will be written",
        )
    ]

    plugin_commands = [
        AacCommand("gen-json", "Converts an AaC model to JSON", print_json, command_arguments)
    ]
    return plugin_commands


@hookimpl
def get_plugin_aac_definitions() -> str:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and definitions defined by the plugin
    """
    return get_resource_file_contents(*plugin_resource_file_args)


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

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
