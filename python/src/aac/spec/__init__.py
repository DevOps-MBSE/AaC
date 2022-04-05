"""Provide access to the core AaC spec."""

from aac.spec.core import get_aac_spec, get_aac_spec_as_yaml, get_primitives, get_root_keys, get_root_fields

__all__ = (
    get_aac_spec.__name__,
    get_aac_spec_as_yaml.__name__,
    get_primitives.__name__,
    get_root_keys.__name__,
    get_root_fields.__name__,
)
