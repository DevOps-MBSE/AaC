"""AaC Plugin implementation module for the aac-gen-design-doc plugin."""

import os

from jinja2 import Template


from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.definition import Definition
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.plugins.validators.required_fields import get_required_fields
from aac.templates.engine import (
    TemplateOutputFile,
    generate_template,
    load_templates,
    write_generated_templates_to_file,
)
from aac.validate import validated_source

plugin_name = "gen-design-doc"


def gen_design_doc(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Generate a System Design Document from Architecture-as-Code models.

    Args:
        architecture_file (str): An AaC file containing the modeled system for which to generate the
                                 System Design document.
        output_directory (str): The directory to which the System Design document will be written.
    """

    def write_design_doc_to_directory():
        parsed_models = _get_parsed_models(architecture_file)

        system_template_file_name = "system-design-doc.md.jinja2"
        loaded_templates = load_templates(__package__)
        selected_template, *_ = [t for t in loaded_templates if system_template_file_name == t.name]

        output_filespec = _get_output_filespec(architecture_file, _get_output_file_extension(system_template_file_name))

        template_properties = _make_template_properties(parsed_models, architecture_file)
        generated_document = _generate_system_doc(output_filespec, selected_template, output_directory, template_properties)
        write_generated_templates_to_file([generated_document])

        return f"Wrote system design document to {os.path.join(output_directory, output_filespec)}"

    with plugin_result(plugin_name, write_design_doc_to_directory) as result:
        return result


def _get_parsed_models(architecture_file: str) -> list[Definition]:
    with validated_source(architecture_file) as result:
        return result.definitions if isinstance(result.definitions, list) else [result.definitions]


def _make_template_properties(parsed_definitions: list[Definition], arch_file: str) -> dict:
    title = _get_document_title(arch_file)
    models = _get_and_prepare_definitions_by_type(parsed_definitions, "model")
    usecases = _get_and_prepare_definitions_by_type(parsed_definitions, "usecase")
    interfaces = _get_and_prepare_definitions_by_type(parsed_definitions, "schema")
    return {
        "title": title,
        "models": models,
        "usecases": usecases,
        "interfaces": interfaces,
    }


def _get_document_title(arch_file: str) -> str:
    filespec, _ = os.path.splitext(arch_file)
    return os.path.basename(filespec)


def _get_output_filespec(filespec: str, ext: str) -> str:
    return f"{_get_document_title(filespec)}_system_design_document{ext}"


def _get_output_file_extension(template_filespec: str) -> str:
    _, extension = os.path.splitext(template_filespec.replace(".jinja2", ""))
    return extension


def _get_and_prepare_definitions_by_type(parsed_definitions: list[Definition], aac_type: str) -> list[dict]:
    def get_definition_structure_with_required_fields(interface_definition: Definition):
        return interface_definition.structure | {"required_fields": get_required_fields(interface_definition)}

    filtered_definitions = get_definitions_by_root_key(aac_type, parsed_definitions)
    definition_template_properties = []
    if aac_type == "schema":
        definition_template_properties = [
            get_definition_structure_with_required_fields(definition) for definition in filtered_definitions
        ]
    else:
        definition_template_properties = [definition.structure for definition in filtered_definitions]

    return definition_template_properties


def _generate_system_doc(
    output_filespec: str, selected_template: Template, output_directory: str, template_properties: dict
) -> TemplateOutputFile:
    template = generate_template(selected_template, output_directory, template_properties)

    template.file_name = output_filespec
    template.overwrite = True
    return template
