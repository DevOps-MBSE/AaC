"""Defines the AaC validator plugin interface via Pluggy Hookspecs."""

from aac.plugins import hookspec


@hookspec
def register_validator() -> str:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and data definitions employed by the plugin
    """
