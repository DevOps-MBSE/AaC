"""An AaC plugin that validates usecase actions are defined behaviors."""

from aac.plugins import hookimpl
from aac.plugins import Plugin, get_plugin_definitions_from_yaml
from aac.plugins.validators.usecase_actions._validate_usecase_actions import (
    PLUGIN_NAME,
    validate_usecase_actions,
)
from aac.plugins.validators import get_plugin_validations_from_definitions


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(PLUGIN_NAME)
    plugin.register_definitions(_get_plugin_definitions())
    plugin.register_definition_validations(_get_plugin_validations())
    return plugin


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "usecase_actions.yaml")


def _get_plugin_validations():
    return get_plugin_validations_from_definitions(_get_plugin_definitions(), validate_usecase_actions)
