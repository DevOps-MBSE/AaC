"""The gen-design-doc plugin module."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.first_party.gen_design_doc.gen_design_doc_impl import gen_design_doc, plugin_name
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
    gen_design_doc_arguments = [
        AacCommandArgument(
            "architecture-file",
            "An AaC file containing the modeled system for which to generate the System Design document.",
            "file",
        ),
        AacCommandArgument(
            "output-directory",
            "The directory to which the System Design document will be written.",
            "directory",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "gen-design-doc",
            "Generate a System Design Document from Architecture-as-Code models.",
            gen_design_doc,
            gen_design_doc_arguments,
        ),
    ]

    return plugin_commands


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "gen_design_doc.yaml")
