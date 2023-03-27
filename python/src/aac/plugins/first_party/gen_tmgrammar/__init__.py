"""The gen_tmgrammar plugin module."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.first_party.gen_tmgrammar.gen_tmgrammar_impl import plugin_name, gen_tmgrammar


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin.register_commands(_get_plugin_commands())
    return plugin


def _get_plugin_commands():
    gen_tmgrammar_arguments = [
        AacCommandArgument(
            "json",
            "Whether to generate the TextMate grammar as a JSON file.",
            "bool",
        ),
        AacCommandArgument(
            "plist",
            "Whether to generate the TextMate grammar as a plist (XML) file.",
            "bool",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "gen-tmgrammar",
            "Generate a TextMate grammar for the AaC VSCode extension.",
            gen_tmgrammar,
            gen_tmgrammar_arguments,
        ),
    ]

    return plugin_commands
