"""A package dealing with AaC persistence."""

import os

from aac.persistence.load import get_language_context_from_state_file


ACTIVE_CONTEXT_STATE_FILE_NAME = os.path.join(os.path.dirname(__file__), "..", "state.json")

__all__ = (
    "ACTIVE_CONTEXT_STATE_FILE_NAME",
    get_language_context_from_state_file.__name__,
)
