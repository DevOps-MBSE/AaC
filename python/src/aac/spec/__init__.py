"""Provide access to the core AaC spec."""

from . import core

__all__ = (
    core.get_aac_spec.__name__,
    core.get_aac_spec_as_yaml.__name__,
    core.get_primitives.__name__,
    core.get_root_keys.__name__,
)
