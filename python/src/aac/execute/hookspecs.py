"""Defines the AaC plugin interface via Pluggy Hookspecs."""

from aac.execute import hookspec


@hookspec
def register_plugin():
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
