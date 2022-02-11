"""Defines the AaC plugin interface via Pluggy Hookspecs."""

from aac import AacCommand
from aac.plugins import hookspec


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
    Return data and ext definitions to apply to the AaC base.

    Returns:
         string representing yaml extensions and data definitions employed by the plugin
    """
