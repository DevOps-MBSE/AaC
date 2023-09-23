"""A package dealing with AaC persistence."""

import os

ACTIVE_CONTEXT_STATE_FILE_NAME = os.path.join(os.path.dirname(__file__), "..", "state.json")

__all__ = ("ACTIVE_CONTEXT_STATE_FILE_NAME",)
