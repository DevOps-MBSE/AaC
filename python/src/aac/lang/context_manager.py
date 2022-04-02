"""This module manages a singleton instance of LanguageContext and its lifecycle."""

from aac.lang.language_context import LanguageContext
from aac.plugins.plugin_manager import get_plugin_definitions
from aac.spec import get_aac_spec

ACTIVE_CONTEXT = None


def get_active_context(reload_context: bool = False) -> LanguageContext:
    """
    Return the current active context instance.

    Args:
        reload_context: If true, the active context will be rebuilt and plugins/extension reapplied.

    Returns:
        The managed instance of LanguageContext
    """

    global ACTIVE_CONTEXT

    if not ACTIVE_CONTEXT or reload_context:
        ACTIVE_CONTEXT = LanguageContext()
        _init_active_context()

    return ACTIVE_CONTEXT


def _init_active_context() -> None:
    """Initialize the active LanguageContext instance with definitions from the core spec and active plugins."""
    active_context = get_active_context()
    active_context.add_definitions_to_context(get_aac_spec())
    active_context.add_definitions_to_context(get_plugin_definitions())
