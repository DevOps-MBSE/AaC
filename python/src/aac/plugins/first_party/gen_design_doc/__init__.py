"""The gen-design-doc plugin module."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.lang.constants import (
    DEFINITION_FIELD_COMMANDS,
    DEFINITION_FIELD_DESCRIPTION,
    DEFINITION_FIELD_DISPLAY,
    DEFINITION_FIELD_HELP_TEXT,
    DEFINITION_FIELD_INPUT,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_TYPE,
)
from aac.lang.definitions.collections import get_definition_by_name
from aac.plugins import Plugin, get_plugin_definitions_from_yaml, hookimpl, register_plugin_command

# I realize this causes a dependency on the gen-plugin plugin
from aac.plugins.first_party.gen_plugin import DEFINITION_FIELD_NUMBER_OF_ARGUMENTS, DEFINITION_FIELD_DEFAULT
from aac.plugins.first_party.gen_design_doc.gen_design_doc_impl import gen_design_doc, plugin_name


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
    definition = get_definition_by_name(plugin_name, _get_plugin_definitions())
    command_structures = definition.get_top_level_fields().get(DEFINITION_FIELD_COMMANDS, []) if definition else []

    plugin_commands = []
    for structure in command_structures:
        arguments = [
            AacCommandArgument(
                name=argument.get(DEFINITION_FIELD_NAME),
                description=argument.get(DEFINITION_FIELD_DESCRIPTION, ""),
                data_type=argument.get(DEFINITION_FIELD_TYPE),
                number_of_arguments=argument.get(DEFINITION_FIELD_NUMBER_OF_ARGUMENTS, 1),
                default=argument.get(DEFINITION_FIELD_DEFAULT),
            )
            for argument in structure.get(DEFINITION_FIELD_INPUT, [])
        ]
        plugin_commands.append(
            AacCommand(
                structure.get(DEFINITION_FIELD_DISPLAY) or structure.get(DEFINITION_FIELD_NAME),
                structure.get(DEFINITION_FIELD_HELP_TEXT, ""),
                # We need to figure out how to get this to work for multiple commands
                gen_design_doc,
                arguments,
            )
        )

        # This doesn't do anything, really, since we're not using it as a decorator.
        register_plugin_command(plugin_name, structure.get(DEFINITION_FIELD_NAME))

    return plugin_commands


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "gen_design_doc.yaml")
