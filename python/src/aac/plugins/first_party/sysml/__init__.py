"""The sysml plugin module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins._common import get_plugin_definitions_from_yaml
from aac.plugins.plugin import Plugin

PLUGIN_NAME = "sysml"

@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(PLUGIN_NAME)
    plugin.register_definitions(_get_plugin_definitions())
    return plugin

def _get_plugin_definitions():
    plugin_definition = get_plugin_definitions_from_yaml(__package__, "sysml_plugin.yaml")
    library_definitions = get_plugin_definitions_from_yaml(__package__, "sysml_lib.yaml")
    return [*plugin_definition, *library_definitions]
