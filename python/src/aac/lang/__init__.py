"""A module that provides AaC language features."""

from aac.lang._active_context import ActiveContext
from aac.lang.context_manager import get_active_context

__all__ = (
    ActiveContext.__name__,
    get_active_context.__name__,
)
