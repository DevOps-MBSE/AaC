"""The material-model plugin module."""

import logging

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.definitions.definition import Definition
from aac.plugins import hookimpl
from aac.plugins.plugin import Plugin, DefinitionValidationContribution
from aac.plugins._common import get_plugin_definitions_from_yaml
from aac.plugins.first_party.material_model.material_model_impl import plugin_name, gen_bom
from aac.plugins.first_party.material_model.referenced_material_exists import (
    VALIDATION_NAME as MATERIAL_REF_VALIDATION_NAME,
    validate_referenced_materials,
)
from aac.plugins.first_party.material_model.no_circular_references import (
    VALIDATION_NAME as CIRCULAR_REF_VALIDATION_NAME,
    validate_no_circluar_material_refs,
)


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
    plugin.register_definitions(_get_plugin_definitions())
    plugin.register_definition_validations(_get_validations(plugin_definitions))
    return plugin


def _get_plugin_commands():
    gen_bom_arguments = [
        AacCommandArgument(
            "architecture-file",
            "The deployment model to convert into a BOM.",
            "str",
        ),
        AacCommandArgument(
            "output-directory",
            "The directory where the BOM file should be placed.",
            "str",
        ),
    ]

    plugin_commands = [
        AacCommand(
            "gen-bom",
            "Generates a CSV Bill of Materials (BOM) from a list of deployment models.",
            gen_bom,
            gen_bom_arguments,
        ),
    ]

    return plugin_commands


def _get_plugin_definitions():
    return get_plugin_definitions_from_yaml(__package__, "material_model.yaml")


def _get_validations(plugin_definitions: list[Definition]) -> list[DefinitionValidationContribution]:
    referenced_material_validation_definition = get_definition_by_name(MATERIAL_REF_VALIDATION_NAME, plugin_definitions)
    no_circular_refs_validation_definition = get_definition_by_name(CIRCULAR_REF_VALIDATION_NAME, plugin_definitions)

    validations = []
    if referenced_material_validation_definition and no_circular_refs_validation_definition:
        referenced_material_validation = DefinitionValidationContribution(
            referenced_material_validation_definition.name,
            referenced_material_validation_definition,
            validate_referenced_materials,
        )
        circular_ref_validation = DefinitionValidationContribution(
            no_circular_refs_validation_definition.name,
            no_circular_refs_validation_definition,
            validate_no_circluar_material_refs,
        )
        validations = [referenced_material_validation, circular_ref_validation]
    else:
        logging.error("Failed to source expected material model validation definitions.")

    return validations
