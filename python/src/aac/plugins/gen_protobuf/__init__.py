"""The gen-protobuf plugin module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.gen_protobuf.gen_protobuf_impl import gen_protobuf
from aac.plugins._common import get_plugin_definitions_from_yaml


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
    plugin.register_definitions(_get_plugin_definitions())
    return plugin


def _get_plugin_commands():
    gen_protobuf_arguments = [
        AacCommandArgument(
            "architecture_file",
            "The yaml file containing the data models to generate as Protobuf messages.",
        ),
        AacCommandArgument(
            "output_directory",
            "The directory to write the generated Protobuf messages to.",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "gen-protobuf",
            "Generate protobuf messages from Arch-as-Code models.",
            gen_protobuf,
            gen_protobuf_arguments,
        ),
    ]

    return plugin_commands


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "gen_protobuf.yaml")
