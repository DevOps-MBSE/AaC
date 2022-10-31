"""The specifications plugin module."""

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.first_party.specifications.specifications_impl import spec_validate
from aac.plugins._common import get_plugin_definitions_from_yaml


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


def _get_plugin_commands():
    spec_validate_arguments = [
        AacCommandArgument(
            "architecture-file",
            "The file to validate for spec cross-references.",
            "file",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "spec-validate",
            "Validates spec traces within the AaC model.",
            spec_validate,
            spec_validate_arguments,
        ),
    ]

    return plugin_commands


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "specifications.yaml")
