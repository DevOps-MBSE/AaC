"""Provide some test utility functions for reducing boilerplate around the use of LanguageContext in tests."""

from aac.lang.language_context import LanguageContext
from aac.lang.definitions.definition import Definition
from aac.spec.core import get_aac_spec


def get_core_spec_context(additional_definitions: list[Definition] = []) -> LanguageContext:
    """Return an initialized language context consisting only of the core spec and any additional definitions passed via arguments."""
    return LanguageContext(get_aac_spec() + additional_definitions)
