"""Defines the AaC plugin interface via Pluggy Hookspecs."""

from aac.plugins import hookspec
from aac.plugins.plugin import Plugin


@hookspec
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
