"""Defines the AaC plugin interface via Pluggy Hookspecs."""

from aac.AacCommand import AacCommand
from aac.plugins import hookspec
from aac.plugins.validators import ValidatorPlugin


@hookspec
def get_commands() -> list[AacCommand]:
    """
    Return a list of AacCommands provided by the plugin to register for use.

    Returns:
        list of AacCommands
    """


@hookspec
def get_plugin_aac_definitions() -> str:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and data definitions employed by the plugin
    """


@hookspec
def register_validators() -> ValidatorPlugin:
    """
    Returns the information about the validation plugin necessary to execute validation.

    Returns:
        A collection of data necessary to manage and execute validation plugins.
    """
