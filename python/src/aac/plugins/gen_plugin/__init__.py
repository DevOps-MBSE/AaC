"""The version plugin module."""

from aac.execute.plugin_runner import AacCommand, AacCommandArgument
from aac.plugins.gen_plugin.gen_plugin_impl import plugin_name, gen_plugin
from aac.execute import hookimpl
from aac.context.language_context import LanguageContext
from aac.lang.plugin import Plugin

@hookimpl
def register_plugin():
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    
    # active_context = LanguageContext()
    # plugin = Plugin(name=plugin_name, commands = _get_plugin_commands())
    
    # active_context.register_plugin(plugin)


def _get_plugin_commands():

    command_arguments = [
        AacCommandArgument(
            "architecture-file",
            "The yaml file containing the AaC DSL of the plugin architecture.",
            "file",
        )
    ]

    plugin_commands = [
        AacCommand(
            "gen-plugin",
            "Generate code and stubs for an AaC plugin.  Overwrites will backup existing files to enable revert-plugin if needed.",
            gen_plugin,
            command_arguments,
        ),
    ]

    return plugin_commands
