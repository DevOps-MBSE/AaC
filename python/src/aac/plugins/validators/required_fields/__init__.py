"""Validation plugin to ensure that each definition has all required fields populated."""

from aac.lang.definitions.definition import Definition
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins._common import get_plugin_definitions_from_yaml
from aac.plugins.validators._common import get_plugin_validations_from_definitions
from aac.plugins.validators.required_fields._validate_required_fields import PLUGIN_NAME, validate_required_fields


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
    return get_plugin_definitions_from_yaml(__package__, "required_fields.yaml")


def _get_plugin_validations():
    return get_plugin_validations_from_definitions(_get_plugin_definitions(), validate_required_fields)


def get_required_fields(definition: Definition) -> list[str]:
    """
    Return a list of field names declared in the definition's Required Fields Validation.

    Args:
        definition (Definition): The definition to search through

    Returns:
        The list of field names declared as required fields in the definition.
    """
    required_validation = [v for v in definition.get_validations() or [] if v.get("name") == PLUGIN_NAME]
    return len(required_validation) == 1 and required_validation[0].get("arguments") or []
