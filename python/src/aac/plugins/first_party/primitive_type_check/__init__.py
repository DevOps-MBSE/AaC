"""The primitive-type-checking plugin module."""

from aac.plugins import hookimpl
from aac.plugins.contributions.contribution_types import PrimitiveValidationContribution
from aac.plugins.first_party.primitive_type_check.validators import (
    plugin_name,
    int_validator,
    bool_validator,
    file_validator,
    num_validator,
    date_validator,
    reference_validator,
    string_validator,
)
from aac.plugins.plugin import Plugin


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin.register_primitive_validations(_get_primitive_validations())
    return plugin


def _get_primitive_validations() -> list[PrimitiveValidationContribution]:
    return [
        int_validator.get_validator(),
        bool_validator.get_validator(),
        file_validator.get_validator(),
        num_validator.get_validator(),
        date_validator.get_validator(),
        reference_validator.get_validator(),
        string_validator.get_validator(),
    ]
