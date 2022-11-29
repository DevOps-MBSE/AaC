"""A package dealing with AaC persistence."""

import os

from aac.persistence.load import get_language_context_from_state_file


__state_file_name__ = os.path.join(os.path.dirname(__file__), "..", "state.json")

__all__ = (
    "__state_file_name__",
    get_language_context_from_state_file.__name__,
)
