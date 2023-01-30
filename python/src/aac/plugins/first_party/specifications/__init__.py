"""The specifications plugin module."""
import logging

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.definitions.definition import Definition
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin, DefinitionValidationContribution
from aac.plugins.first_party.specifications.specifications_impl import plugin_name, spec_csv
from aac.plugins.first_party.specifications.globally_unique_id import validate_unique_ids
from aac.plugins.first_party.specifications.referenced_ids_exist import validate_referenced_ids
from aac.plugins._common import get_plugin_definitions_from_yaml


@hookimpl
def get_plugin() -> Plugin:
    """
    Returns information about the plugin.

    Returns:
        A collection of information about the plugin and what it contributes.
    """
    plugin = Plugin(plugin_name)
    plugin_definitions = _get_plugin_definitions()
    plugin.register_commands(_get_plugin_commands())
    plugin.register_definitions(plugin_definitions)
    plugin.register_definition_validations(_get_validations(plugin_definitions))
    logging.info("Spec plugin created.")

    return plugin


def _get_plugin_commands():
    spec_csv_arguments = [
        AacCommandArgument(
            "architecture-file",
            "The spec file to convert to csv.",
            "file",
        ),
        AacCommandArgument(
            "output-directory",
            "Output directory for the CSV formatted spec file",
            "directory",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "spec-csv",
            "Generates a comma separated value file (i.e. Excel file) listing requirements.",
            spec_csv,
            spec_csv_arguments,
        ),
    ]

    return plugin_commands


def _get_plugin_definitions() -> list[Definition]:
    return get_plugin_definitions_from_yaml(__package__, "specifications.yaml")


def _get_validations(plugin_definitions: list[Definition]) -> list[DefinitionValidationContribution]:
    global_id_validation_definition = get_definition_by_name("Requirement ID is unique", plugin_definitions)
    id_exists_validation_definition = get_definition_by_name("Referenced IDs exist", plugin_definitions)

    validations = []
    if global_id_validation_definition and id_exists_validation_definition:
        global_id_validation = DefinitionValidationContribution(global_id_validation_definition.name, global_id_validation_definition, validate_unique_ids)
        id_exists_validation = DefinitionValidationContribution(id_exists_validation_definition.name, id_exists_validation_definition, validate_referenced_ids)
        validations = [global_id_validation, id_exists_validation]
    else:
        logging.error("Failed to source expected specification validation definitions.")

    return validations
