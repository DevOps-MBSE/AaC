"""The version plugin module."""

from os.path import join, dirname
from aac.execute.plugin_runner import AacCommand, AacCommandArgument
from aac.plugins.generate.generate_impl import plugin_name, gen_plugin
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
# from aac.lang.plugin import Plugin
from aac.execute.plugin_runner import PluginRunner

GEN_PLUGIN_AAC_FILE_NAME = "gen_plugin.aac"

@hookimpl
def register_plugin() -> None:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    
    active_context = LanguageContext()
    gen_plugin_aac_file = join(dirname(__file__), GEN_PLUGIN_AAC_FILE_NAME)
    definitions = active_context.parse_and_load(gen_plugin_aac_file)
    
    gen_plugin_plugin_definition = [definition for definition in definitions if definition.name == plugin_name][0]

    plugin_instance = gen_plugin_plugin_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)
    
    plugin_runner = PluginRunner(plugin_definition=gen_plugin_plugin_definition)
    plugin_runner.add_command_callback("gen-plugin", gen_plugin)
    
    active_context.register_plugin_runner(plugin_runner)
