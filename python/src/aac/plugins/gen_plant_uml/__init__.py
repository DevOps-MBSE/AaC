"""Generated AaC Plugin hookimpls module for the aac-plantuml plugin."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from aac.AacCommand import AacCommand, AacCommandArgument
from aac.package_resources import get_resource_file_contents
from aac.plugins import hookimpl
from aac.plugins.gen_plant_uml.gen_plant_uml_impl import puml_component, puml_sequence, puml_object


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Return a list of AacCommands provided by the plugin to register for use.

    This function is automatically generated. Do not edit.

    Returns:
        list of AacCommands
    """
    puml_component_arguments = [
        AacCommandArgument(
            "architecture_file",
            "Path to a yaml file containing an AaC usecase from which to generate a Plant UML component diagram.",
        ),
        AacCommandArgument(
            "--output_directory",
            "Output directory for the PlantUML (.puml) diagram file",
        )
    ]
    puml_sequence_arguments = [
        AacCommandArgument(
            "architecture_file",
            "Path to a yaml file containing an AaC usecase from which to generate a Plant UML sequence diagram.",
        ),
        AacCommandArgument(
            "--output_directory",
            "Output directory for the PlantUML (.puml) diagram file",
        )
    ]
    puml_object_arguments = [
        AacCommandArgument(
            "architecture_file",
            "Path to a yaml file containing an AaC usecase from which to generate a Plant UML object diagram.",
        ),
        AacCommandArgument(
            "--output_directory",
            "Output directory for the PlantUML (.puml) diagram file",
        )
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


@hookimpl
def get_base_model_extensions() -> str:
    """
    Returns the CommandBehaviorType modeling language extension to the plugin infrastructure.

    Returns:
        string representing yaml extensions and data definitions employed by the plugin
    """
    return get_resource_file_contents(__package__, "gen_plant_uml.yaml")
