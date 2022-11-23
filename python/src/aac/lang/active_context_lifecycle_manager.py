"""This module manages a singleton instance of LanguageContext and its lifecycle."""

import json

from typing import Optional

from aac import __state_file_name__
from aac.io.writer import write_file
from aac.lang.language_context import LanguageContext
from aac.lang.language_context_encoder import LanguageContextEncoder
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
        ACTIVE_CONTEXT = load_language_context(__state_file_name__) or get_initialized_language_context()

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


def write_language_context(file_name: str, language_context: Optional[LanguageContext] = None) -> None:
    """
    Write the language context to disk.

    Args:
        file_name (str): The name of the file in which to store the language context.
        language_context (Optional[LanguageContext]): The language context to be written. If not
            provided, the active context will be used.
    """
    content = json.dumps(language_context or get_active_context(), cls=LanguageContextEncoder)
    write_file(file_name, content, True)


def load_language_context(file_name: str) -> Optional[LanguageContext]:
    """
    Load the language context from filename.

    Args:
        file_name (str): The name of the file from which to load the language context.

    Returns:
        A language context object loaded from the file, if it exists; otherwise, None.
    """
    try:
        with open(file_name) as state_file:
            return json.loads(state_file.read())
    except FileNotFoundError:
        pass
