"""This module manages a singleton instance of LanguageContext and its lifecycle."""

import json

from os.path import lexists
from typing import Optional

from aac.io.writer import write_file
from aac.lang.language_context import LanguageContext
from aac.persistence import ACTIVE_CONTEXT_STATE_FILE_NAME, get_language_context_from_state_file
from aac.plugins.plugin_manager import get_plugins
from aac.serialization.language_context_encoder import LanguageContextEncoder
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
        ACTIVE_CONTEXT = load_language_context(ACTIVE_CONTEXT_STATE_FILE_NAME, reload_context)

    return ACTIVE_CONTEXT


def load_language_context(file_name: str, reload_context: bool = False) -> LanguageContext:
    """
    Load the language context from filename.

    Args:
        file_name (str): The name of the file from which to load the language context.
        reload_context (bool): If True, a fresh active context will be returned; otherwise, the
            active context will be loaded from the provided file URI if it exists.

    Returns:
        A language context object loaded from the file, if it exists; otherwise, None.
    """
    if lexists(file_name) and not reload_context:
        return get_language_context_from_state_file(file_name)
    else:
        return get_initialized_language_context()


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


def write_language_context(file_name: str, language_context: Optional[LanguageContext] = None) -> None:
    """
    Write the language context to disk.

    Args:
        file_name (str): The name of the file in which to store the language context.
        language_context (Optional[LanguageContext]): The language context to be written. If not
            provided, the active context will be used.
    """
    content = json.dumps(language_context or get_active_context(), cls=LanguageContextEncoder, indent=2)
    write_file(file_name, content, True)
