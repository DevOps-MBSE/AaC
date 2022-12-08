"""This module manages a singleton instance of LanguageContext and its lifecycle."""

from aac.lang.language_context import LanguageContext
from aac.persistence import ACTIVE_CONTEXT_STATE_FILE_NAME
from aac.plugins.plugin_manager import get_plugins
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

    if not ACTIVE_CONTEXT:
        if reload_context:
            ACTIVE_CONTEXT = get_initialized_language_context()
        else:
            ACTIVE_CONTEXT = LanguageContext()
            ACTIVE_CONTEXT.import_from_file(ACTIVE_CONTEXT_STATE_FILE_NAME)

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
        language_context.activate_plugins(get_plugins())

    return language_context
