"""Validation plugin to ensure that each definition has all required fields populated."""

from aac.lang.definitions.definition import Definition
from aac.package_resources import get_resource_file_contents, get_resource_file_path
from aac.parser import parse
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin
from aac.plugins.validators import ValidatorPlugin, get_validation_definition_from_plugin_definitions
from aac.plugins.validators.required_fields._validate_required_fields import validate_required_fields


PLUGIN_YAML_FILE = "required_fields.yaml"
plugin_resource_file_args = (__package__, PLUGIN_YAML_FILE)


@hookimpl
def get_plugin_aac_definitions() -> str:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and definitions defined by the plugin
    """
    return get_resource_file_contents(*plugin_resource_file_args)


@hookimpl
def register_validators() -> ValidatorPlugin:
    """
    Returns the information about the validation plugin necessary to execute validation.

    Returns:
        A collection of data necessary to manage and execute validation plugins.
    """
    validation_definition = get_validation_definition_from_plugin_definitions(get_plugin_aac_definitions())
    return ValidatorPlugin(validation_definition.name, validation_definition, validate_required_fields)


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


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns the information about plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin_definitions = parse(
        get_plugin_aac_definitions(),
        get_resource_file_path(*plugin_resource_file_args)
    )

    *_, plugin_name = __package__.split(".")
    plugin = Plugin(plugin_name)
    plugin.register_definitions(set(plugin_definitions))
    plugin.register_validations({register_validators()})

    return plugin


REQUIRED_FIELDS_VALIDATION_STRING = register_validators().name
