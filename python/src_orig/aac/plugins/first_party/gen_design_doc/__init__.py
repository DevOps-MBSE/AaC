"""The gen-design-doc plugin module."""

from aac.plugins import Plugin, get_plugin_commands_from_definitions, get_plugin_definitions_from_yaml, hookimpl
from aac.plugins.first_party.gen_design_doc.gen_design_doc_impl import plugin_name


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)

    definitions = get_plugin_definitions_from_yaml(__package__, "gen_design_doc.yaml")
    plugin.register_commands(get_plugin_commands_from_definitions(plugin_name, definitions))
    plugin.register_definitions(definitions)
    return plugin
