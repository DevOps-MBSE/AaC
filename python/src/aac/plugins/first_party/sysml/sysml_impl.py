"""AaC Plugin implementation module for the sysml plugin."""

import logging
import os
from typing import Callable, Optional
from aac.io.paths import sanitize_filesystem_path
from aac.io.writer import write_definitions_to_file
from aac.lang.constants import DEFINITION_FIELD_COMPONENTS, DEFINITION_FIELD_TYPE
from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.schema import get_definition_schema
from aac.validate import validated_source

from aac.plugins.first_party.sysml.constants import (
    SYSML_DEFINITION_FIELD_BLOCKS,
    SYSML_DEFINITION_FIELD_SYSML_ELEMENT,
    SYSML_DEFINITION_NAME_BDD,
    SYSML_DEFINITION_NAME_BLOCK,
)
from aac.plugins.first_party.sysml.sysml_definition_builder import (
    create_block,
    create_block_definition_diagram,
    create_model,
    create_field_entry,
)
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

plugin_name = "sysml"
GENERATED_FILE_SUFFIX_CORE = "CORE"
GENERATED_FILE_SUFFIX_SYSML = "SYSML"


def sysml_to_aac(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Start a RESTful interface for interacting with and managing AaC.

    Args:
        architecture_file (str): Path to a yaml file containing a model or modeled system written in the AaC SysML DSL.
        output_directory (str): Output directory for generated core AaC model(s).
    """

    def convert_sysml_to_aac():
        output_file = _get_output_file_name(architecture_file, output_directory, GENERATED_FILE_SUFFIX_CORE)
        _convert_between_aac_dsls(architecture_file, output_file, _convert_sysml_definition_to_aac_core_definition)
        return f"Successfully converted the SysML AaC file to the Core spec in {output_file}"

    with plugin_result(plugin_name, convert_sysml_to_aac) as result:
        return result


def aac_to_sysml(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Start a RESTful interface for interacting with and managing AaC.

    Args:
        architecture_file (str): Path to a yaml file containing a model or modeled system written in the core AaC DSL.
        output_directory (str): Output directory for generated SysML AaC model(s).
    """

    def convert_aac_to_sysml():
        output_file = _get_output_file_name(architecture_file, output_directory, GENERATED_FILE_SUFFIX_SYSML)
        _convert_between_aac_dsls(architecture_file, output_file, _convert_aac_core_definition_to_sysml_definition)
        return f"Successfully converted the SysML AaC file to the Core spec in {output_file}"

    with plugin_result(plugin_name, convert_aac_to_sysml) as result:
        return result


def _convert_between_aac_dsls(architecture_file: str, output_file: str, conversion_function: Callable):
    active_context = get_active_context()
    sanitized_arch_file = sanitize_filesystem_path(architecture_file)

    with validated_source(sanitized_arch_file) as result:
        converted_definitions = [conversion_function(definition, active_context) for definition in result.definitions]
        converted_definitions = [definition for definition in converted_definitions if definition is not None]
        write_definitions_to_file(converted_definitions, output_file)


def _convert_aac_core_definition_to_sysml_definition(
    definition_to_convert: Definition, language_context: LanguageContext
) -> Optional[Definition]:
    """
    Converts an AaC core definition with SysML metadata to SysML AaC Definition.

    Args:
        definition_to_convert (Definition): The Core AaC definition to convert to a SysML definition
        language_context (LanguageContext): The language context used to look-up referenced definitions

    Returns:
        A SysML definition populated via content from the core spec definition, or None if the conversion isn't supported.
    """

    def _get_corresponding_sysml_definition() -> Optional[Definition]:
        definition_fields = definition_to_convert.get_top_level_fields()
        sysml_definition = language_context.get_definition_by_name(definition_fields.get(SYSML_DEFINITION_FIELD_SYSML_ELEMENT))

        if SYSML_DEFINITION_FIELD_SYSML_ELEMENT not in definition_fields:
            logging.error(
                f"AaC core definition '{definition_to_convert.name}' doesn't have the requisite SysML mapping in field '{SYSML_DEFINITION_FIELD_SYSML_ELEMENT}'"
            )

        return sysml_definition

    def _convert_definition(sysml_target: Definition) -> Optional[Definition]:
        name = definition_to_convert.name
        sysml_definition = None
        if sysml_target.name == SYSML_DEFINITION_NAME_BDD:

            # Components and blocks are both 1:1 references
            components: list = definition_to_convert.get_top_level_fields().get(DEFINITION_FIELD_COMPONENTS, [])
            blocks = [component.get(DEFINITION_FIELD_TYPE) for component in components]
            sysml_definition = create_block_definition_diagram(name, "", blocks)

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


def _convert_sysml_definition_to_aac_core_definition(
    definition_to_convert: Definition, language_context: LanguageContext
) -> Optional[Definition]:
    """
    Converts a SysML AaC Definition to an AaC core definition with SysML metadata.

    Args:
        definition_to_convert (Definition): The SysML definition to convert to a Core AaC definition
        language_context (LanguageContext): The language context used to look-up referenced definitions

    Returns:
        A Core AaC definition populated via content from the SysML definition including associated metadata, or None if the conversion isn't supported.
    """
    definition_to_convert_schema = get_definition_schema(definition_to_convert, language_context)
    definition_to_return = None

    if definition_to_convert_schema:
        if definition_to_convert_schema.name == SYSML_DEFINITION_NAME_BDD:
            # Components and blocks are both references, but the components structure leverages fields
            referenced_blocks: list = definition_to_convert.get_top_level_fields().get(SYSML_DEFINITION_FIELD_BLOCKS, [])
            component_fields = []
            for block_name in referenced_blocks:
                field_name = block_name[0].lower() + block_name[1:]
                component_fields.append(create_field_entry(field_name, block_name, ""))
            definition_to_return = create_model(definition_to_convert.name, "", component_fields)

        elif definition_to_convert_schema.name == SYSML_DEFINITION_NAME_BLOCK:
            definition_to_return = create_model(definition_to_convert.name, "")

        else:
            logging.error(f"There is no conversion available for the SysML definition '{definition_to_convert_schema.name}'")

        # Add the source SysML definition to the metadata
        if definition_to_return:
            definition_to_return.get_top_level_fields()[
                SYSML_DEFINITION_FIELD_SYSML_ELEMENT
            ] = definition_to_convert_schema.name

    else:
        logging.error(f"Unable to find the schema definition for the SysML definition '{definition_to_convert.name}'")

    return definition_to_return


def _get_output_file_name(source_file: str, output_directory: str, conversion_suffix: str) -> str:
    sanitized_source_file = sanitize_filesystem_path(source_file)
    sanitized_output_dir = sanitize_filesystem_path(output_directory)
    file_name, file_ext = os.path.splitext(os.path.basename(sanitized_source_file))
    output_file_name = f"{file_name}_{conversion_suffix}{file_ext}"
    return os.path.join(sanitized_output_dir, output_file_name)
