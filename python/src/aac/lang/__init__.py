"""A module that provides AaC language features."""

from .context_manager import get_active_context
from .ActiveContext import ActiveContext

__all__ = (
    get_active_context.__name__,
    ActiveContext.__name__,
)
