"""Generated AaC Plugin hookimpls module for the aac-gen-gherkin-behaviors plugin."""
# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.package_resources import get_resource_file_contents, get_resource_file_path
from aac.io.parser import parse
from aac.plugins import hookimpl
from aac.plugins.gen_gherkin_behaviors.gen_gherkin_behaviors_impl import gen_gherkin_behaviors
from aac.plugins.plugin import Plugin


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_commands(_get_plugin_commands())
    plugin.register_definitions(_get_plugin_definitions())
    return plugin


def _get_plugin_definitions():
    plugin_resource_file_args = (__package__, "gen_gherkin_behaviors.yaml")
    plugin_definitions = parse(
        get_resource_file_contents(*plugin_resource_file_args),
        get_resource_file_path(*plugin_resource_file_args)
    )
    return plugin_definitions


def _get_plugin_commands() -> list[AacCommand]:
    gen_gherkin_behaviors_arguments = [
        AacCommandArgument(
            "architecture_file",
            "The yaml file containing the data models to generate as Gherkin feature files.",
        ),
        AacCommandArgument(
            "output_directory",
            "The directory to write the generated Gherkin feature files to.",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "gen-gherkin-behaviors",
            "Generate Gherkin feature files from Arch-as-Code model behavior scenarios.",
            gen_gherkin_behaviors,
            gen_gherkin_behaviors_arguments,
        ),
    ]

    return plugin_commands
