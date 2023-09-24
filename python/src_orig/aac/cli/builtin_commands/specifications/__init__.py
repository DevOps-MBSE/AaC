"""The specifications plugin module."""

from aac.execute.plugin_runner import AacCommand, AacCommandArgument
from aac.lang.definitions.definition import Definition
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.cli.builtin_commands.specifications.specifications_impl import plugin_name, spec_csv
from aac.plugins._common import get_plugin_definitions_from_yaml


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin_definitions = _get_plugin_definitions()
    plugin.register_commands(_get_plugin_commands())
    plugin.register_definitions(plugin_definitions)

    return plugin


def _get_plugin_commands():
    spec_csv_arguments = [
        AacCommandArgument(
            "architecture-file",
            "The spec file to convert to csv.",
            "file",
        ),
        AacCommandArgument(
            "output-directory",
            "Output directory for the CSV formatted spec file",
            "directory",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "spec-csv",
            "Generates a comma separated value file (i.e. Excel file) listing requirements.",
            spec_csv,
            spec_csv_arguments,
        ),
    ]

    return plugin_commands


def _get_plugin_definitions() -> list[Definition]:
    return get_plugin_definitions_from_yaml(__package__, "specifications.yaml")
