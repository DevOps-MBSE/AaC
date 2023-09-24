"""The version plugin module."""

from os.path import join, dirname
from aac.execute.plugin_runner import AacCommand
from aac.plugins.version.version_impl import plugin_name, version
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.execute.plugin_runner import PluginRunner
from aac.lang.plugin import Plugin

VERSION_AAC_FILE_NAME = "version.aac"

@hookimpl
def register_plugin() -> None:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    
    active_context = LanguageContext()
    version_aac_file = join(dirname(__file__), VERSION_AAC_FILE_NAME)
    definitions = active_context.parse_and_load(version_aac_file)
    
    version_plugin_definition = [definition for definition in definitions if definition.name == plugin_name][0]

    plugin_instance: Plugin = version_plugin_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)
    
    plugin_runner = PluginRunner(plugin_name=plugin_name, plugin_definition=version_plugin_definition, commands = _get_plugin_commands())
    
    active_context.register_plugin_runner(plugin_runner)


def _get_plugin_commands():
    plugin_commands = [
        AacCommand(
            "version",
            "Print the AaC package version.",
            version,
        ),
    ]

    return plugin_commands
