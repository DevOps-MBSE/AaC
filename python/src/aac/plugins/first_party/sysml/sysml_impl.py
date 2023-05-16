"""AaC Plugin implementation module for the sysml plugin."""

import logging
from typing import Optional
from aac.lang.constants import DEFINITION_FIELD_COMPONENTS, DEFINITION_NAME_MODEL
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.schema import get_definition_schema

from aac.plugins.first_party.sysml.constants import SYSML_DEFINITION_FIELD_BLOCKS, SYSML_DEFINITION_FIELD_SYSML_ELEMENT, SYSML_DEFINITION_NAME_BDD, SYSML_DEFINITION_NAME_BLOCK
from aac.plugins.first_party.sysml.sysml_definition_builder import create_block, create_block_definition_diagram, create_model
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

plugin_name = "sysml"


def sysml_to_aac(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Start a RESTful interface for interacting with and managing AaC.

    Args:
        architecture_file (str): Path to a yaml file containing a model or modeled system written in the AaC SysML DSL.
        output_directory (str): Output directory for generated core AaC model(s).
    """
    def convert_sysml_to_aac():
        pass

    with plugin_result(plugin_name, convert_sysml_to_aac, architecture_file, output_directory) as result:
        return result

def aac_to_sysml(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Start a RESTful interface for interacting with and managing AaC.

    Args:
        architecture_file (str): Path to a yaml file containing a model or modeled system written in the core AaC DSL.
        output_directory (str): Output directory for generated SysML AaC model(s).
    """
    def convert_aac_to_sysml():
        pass

    with plugin_result(plugin_name, convert_aac_to_sysml, architecture_file, output_directory) as result:
        return result

def convert_aac_core_definition_to_sysml_definition(definition_to_convert: Definition, language_context: LanguageContext) -> Optional[Definition]:
    """
    Converts an AaC core definition with SysML metadata to SysML AaC Definition.

    Args:
        TODO

    Returns:
        A SysML definition populated via content from the core spec definition, or None if the conversion isn't supported.
    """

    def _get_corresponding_sysml_definition() -> Optional[Definition]:
        definition_fields = definition_to_convert.get_top_level_fields()
        sysml_definition = language_context.get_definition_by_name(definition_fields.get(SYSML_DEFINITION_FIELD_SYSML_ELEMENT))

        if SYSML_DEFINITION_FIELD_SYSML_ELEMENT not in definition_fields:
            logging.error(f"AaC core definition '{definition_to_convert.name}' doesn't have the requisite SysML mapping in field '{SYSML_DEFINITION_FIELD_SYSML_ELEMENT}'")

        return sysml_definition

    def _convert_definition(sysml_target: Definition) -> Optional[Definition]:
        name = definition_to_convert.name
        sysml_definition = None
        if sysml_target.name == SYSML_DEFINITION_NAME_BDD:

            # Components and blocks are both 1:1 references
            blocks = definition_to_convert.get_top_level_fields().get(DEFINITION_FIELD_COMPONENTS, [])
            sysml_definition = create_block_definition_diagram(name, blocks)

        elif sysml_target.name == SYSML_DEFINITION_NAME_BLOCK:
            sysml_definition = create_block(name)

        else:
            logging.error(f"SysML definition '{sysml_target.name}' conversion isn't supported.")

        return sysml_definition

    target_sysml_definition = _get_corresponding_sysml_definition()
    definition_to_return = None

    if target_sysml_definition:
        converted_definition = _convert_definition(target_sysml_definition)

        if converted_definition:
            definition_to_return = converted_definition

    return definition_to_return

def convert_sysml_definition_to_aac_core_definition(definition_to_convert: Definition) -> Optional[Definition]:
    """
    Converts a SysML AaC Definition to an AaC core definition with SysML metadata.

    Args:
        TODO
    """
    definition_to_convert_schema = get_definition_schema(definition_to_convert)
    definition_to_return = None

    if definition_to_convert_schema.name == SYSML_DEFINITION_NAME_BDD:
        name = definition_to_convert.name
        # Components and blocks are both 1:1 references
        blocks = definition_to_convert.get_top_level_fields().get(SYSML_DEFINITION_FIELD_BLOCKS, [])
        definition_to_return = create_model(name, "", blocks)

    elif definition_to_convert_schema.name == SYSML_DEFINITION_NAME_BLOCK:
        name = definition_to_convert.name
        definition_to_return = create_model(name, "")

    else:
        logging.error(f"There is no conversion available for the SysML definition '{definition_to_convert_schema.name}'")

    return definition_to_return
