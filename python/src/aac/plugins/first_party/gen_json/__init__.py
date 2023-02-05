"""Generated AaC Plugin hookimpls module for the aac-gen-json plugin."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.first_party.gen_json.gen_json_impl import print_json, plugin_name
from aac.plugins.plugin import Plugin
from aac.plugins._common import get_plugin_definitions_from_yaml


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin.register_commands(_get_plugin_commands())
    plugin.register_definitions(_get_plugin_definitions())
    return plugin


def _get_plugin_commands():
    command_arguments = [
        AacCommandArgument(
            "architecture-files",
            "File paths to AaC file(s) containing models to parse and print as JSON.",
            "file",
            number_of_arguments=-1,
        ),
        AacCommandArgument(
            "--output-directory",
            "Directory in which JSON files will be written",
            "directory",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "gen-json",
            "Convert an AaC definition to JSON",
            print_json,
            command_arguments,
        )
    ]

    return plugin_commands


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "gen_json.yaml")
