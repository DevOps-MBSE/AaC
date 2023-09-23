"""Generated AaC Plugin hookimpls module for the gen-plant-uml plugin."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.first_party.gen_plant_uml.gen_plant_uml_impl import plugin_name, puml_component, puml_sequence, puml_object
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
    puml_component_arguments = [
        AacCommandArgument(
            "architecture-file",
            "Path to a yaml file containing an AaC usecase from which to generate a Plant UML component diagram.",
            "file",
        ),
        AacCommandArgument(
            "output-directory",
            "Output directory for the PlantUML (.puml) diagram file",
            "directory",
        ),
    ]

    puml_sequence_arguments = [
        AacCommandArgument(
            "architecture-file",
            "Path to a yaml file containing an AaC usecase from which to generate a Plant UML sequence diagram.",
            "file",
        ),
        AacCommandArgument(
            "output-directory",
            "Output directory for the PlantUML (.puml) diagram file",
            "directory",
        ),
    ]

    puml_object_arguments = [
        AacCommandArgument(
            "architecture-file",
            "Path to a yaml file containing an AaC usecase from which to generate a Plant UML object diagram.",
            "file",
        ),
        AacCommandArgument(
            "output-directory",
            "Output directory for the PlantUML (.puml) diagram file",
            "directory",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "puml-component",
            "Converts an AaC model to a Plant UML component diagram.",
            puml_component,
            puml_component_arguments,
        ),
        AacCommand(
            "puml-sequence",
            "Converts an AaC usecase to a Plant UML sequence diagram.",
            puml_sequence,
            puml_sequence_arguments,
        ),
        AacCommand(
            "puml-object",
            "Converts an AaC model to a Plant UML object diagram.",
            puml_object,
            puml_object_arguments,
        ),
    ]

    return plugin_commands


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "gen_plant_uml.yaml")
