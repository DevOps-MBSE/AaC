"""The specifications plugin module."""
import logging

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.first_party.specifications.specifications_impl import plugin_name, spec_csv
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
    logging.warn("Spec plugin created.")
    return plugin


def _get_plugin_commands():
    spec_csv_arguments = [
        AacCommandArgument(
            "architecture-file",
            "The spec file to convert to csv.",
            "file",
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


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "specifications.yaml")
