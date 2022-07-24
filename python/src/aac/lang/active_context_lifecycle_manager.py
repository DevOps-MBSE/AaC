"""This module manages a singleton instance of LanguageContext and its lifecycle."""

from aac.lang.language_context import LanguageContext
from aac.plugins.plugin_manager import get_plugin_definitions, get_plugins
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
        ACTIVE_CONTEXT = get_initialized_language_context()

    return ACTIVE_CONTEXT


def get_initialized_language_context(core_spec_only: bool = False) -> LanguageContext:
    """
    Return a LanguageContext that has been initialized with the core AaC spec and active plugins.

    Args:
        core_spec_only (bool): True if only the LanguageContext should be populated with only the core spec
    """
    language_context = LanguageContext()
    language_context.add_definitions_to_context(get_aac_spec())

    if not core_spec_only:
        language_context.add_plugins(get_plugins())
        language_context.add_definitions_to_context(get_plugin_definitions())

    return language_context
