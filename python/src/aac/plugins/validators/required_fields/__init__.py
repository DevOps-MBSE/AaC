"""Validation plugin to ensure that each definition has all required fields populated."""

from aac.io.parser import parse
from aac.lang.definitions.definition import Definition
from aac.package_resources import get_resource_file_contents, get_resource_file_path
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.validators import ValidatorPlugin, get_validation_definition_from_plugin_definitions
from aac.plugins.validators.required_fields._validate_required_fields import validate_required_fields


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_definitions(_get_plugin_definitions())
    plugin.register_validations(_get_plugin_validations())
    return plugin


def _get_plugin_definitions():
    plugin_resource_file_args = (__package__, "required_fields.yaml")
    plugin_definitions = parse(
        get_resource_file_contents(*plugin_resource_file_args),
        get_resource_file_path(*plugin_resource_file_args)
    )
    return plugin_definitions


def _get_plugin_validations():
    validation_definition = get_validation_definition_from_plugin_definitions(_get_plugin_definitions())
    return [
        ValidatorPlugin(validation_definition.name, validation_definition, validate_required_fields)
    ]


def get_required_fields(definition: Definition) -> list[str]:
    """
    Return a list of field names declared in the definition's Required Fields Validation.

    Args:
        definition (Definition): The definition to search through

    Returns:
        The list of field names declared as required fields in the definition.
    """
    required_validation = [v for v in definition.get_validations() if v.get("name") == REQUIRED_FIELDS_VALIDATION_STRING]
    return required_validation and required_validation[0].get("arguments") or []


REQUIRED_FIELDS_VALIDATION_STRING = _get_plugin_validations()[0].name
