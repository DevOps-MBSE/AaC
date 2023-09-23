"""Defines the AaC plugin interface via Pluggy Hookspecs."""

from aac.cli import hookspec


@hookspec
def get_plugin() -> str:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
