"""This module manages the ActiveContext instance and its lifecycle."""

from aac.lang import ActiveContext
from aac.plugins import get_plugin_definitions
from aac.spec import get_aac_spec

ACTIVE_CONTEXT = None


def get_active_context(reload_context: bool = False) -> ActiveContext:
    """
    Return the current active context instance.

    Args:
        reload_context: If true, the active context will be reconstructed if an active context instance already exists.

    Returns:
        An instance of the ActiveContext
    """

    global ACTIVE_CONTEXT

    if not ACTIVE_CONTEXT or reload_context:
        ACTIVE_CONTEXT = ActiveContext()
        _init_active_context()

    return ACTIVE_CONTEXT


def _init_active_context() -> None:
    """Initialize the ActiveContext instance with definitions from the core spec and active plugins."""
    active_context = get_active_context()
    active_context.add_definitions_to_context(get_aac_spec())
    active_context.add_definitions_to_context(get_plugin_definitions())
