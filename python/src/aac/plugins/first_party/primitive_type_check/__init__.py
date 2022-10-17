"""The primitive-type-checking plugin module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

from aac.plugins import hookimpl
from aac.plugins.first_party.primitive_type_check.type_validations import INTEGER_VALIDATOR
from aac.plugins.contributions.contribution_types import TypeValidationContribution
from aac.plugins.plugin import Plugin


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_primitive_validations(_get_primitive_validations())
    return plugin


def _get_primitive_validations() -> list[TypeValidationContribution]:
    return [INTEGER_VALIDATOR]
