"""A module that provides AaC language features."""

from ._active_context import ActiveContext
from .context_manager import get_active_context

__all__ = (
    ActiveContext.__name__,
    get_active_context.__name__,
)
