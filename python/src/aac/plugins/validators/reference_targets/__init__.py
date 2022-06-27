"""Validation plugin to ensure that each definition has all required fields populated."""

from aac.lang.definitions.definition import Definition
from aac.package_resources import get_resource_file_contents
from aac.plugins import hookimpl
from aac.plugins.validators import ValidatorPlugin, get_validation_definition_from_plugin_definitions
from aac.plugins.validators.reference_targets._validate_reference_targets import validate_reference_targets

PLUGIN_YAML_FILE = "reference_targets.yaml"


@hookimpl
def get_plugin_aac_definitions() -> str:
    """
    Return the plugins Aac definitions.

    Returns:
         string representing yaml extensions and definitions defined by the plugin
    """
    return get_resource_file_contents(__package__, PLUGIN_YAML_FILE)


@hookimpl
def register_validators() -> ValidatorPlugin:
    """
    Returns the information about the validation plugin necessary to execute validation.

    Returns:
        A collection of data necessary to manage and execute validation plugins.
    """
    validation_definition = get_validation_definition_from_plugin_definitions(get_plugin_aac_definitions())
    return ValidatorPlugin(validation_definition.name, validation_definition, validate_reference_targets)


def get_reference_fields(definition: Definition) -> list[str]:
    """
    Return a list of field names declared in the definition's Reference Target Validation.

    Args:
        definition (Definition): The definition to search through

    Returns:
        The list of field names declared as required fields in the definition.
    """
    reference_validation = [v for v in definition.get_validations() if v.get("name") == REFERENCE_FIELDS_VALIDATION_STRING]
    return reference_validation and reference_validation[0].get("arguments") or []


REFERENCE_FIELDS_VALIDATION_STRING = register_validators().name
