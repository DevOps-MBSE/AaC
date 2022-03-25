"""This module manages the Active Context instance and its lifecycle."""

from aac.lang import ActiveContext

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

    return ACTIVE_CONTEXT
