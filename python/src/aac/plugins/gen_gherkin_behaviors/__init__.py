"""Generated AaC Plugin hookimpls module for the aac-gen-gherkin-behaviors plugin."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.package_resources import get_resource_file_contents
from aac.plugins import hookimpl
from aac.plugins.gen_gherkin_behaviors.gen_gherkin_behaviors_impl import gen_gherkin_behaviors


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Return a list of AacCommands provided by the plugin to register for use.

    This function is automatically generated. Do not edit.

    Returns:
        list of AacCommands
    """
    gen_gherkin_behaviors_arguments = [
        AacCommandArgument("architecture_file", "The yaml file containing the data models to generate as Gherkin feature files."),
        AacCommandArgument("output_directory", "The directory to write the generated Gherkin feature files to."),
    ]

    plugin_commands = [
        AacCommand(
            "gen-gherkin-behaviors",
            "Generate Gherkin feature files from Arch-as-Code model behavior scenarios.",
            gen_gherkin_behaviors,
            gen_gherkin_behaviors_arguments),
    ]

    return plugin_commands


@hookimpl
def get_plugin_aac_definitions() -> str:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and definitions defined by the plugin
    """

    return get_resource_file_contents(__package__, "gen_gherkin_behaviors.yaml")
