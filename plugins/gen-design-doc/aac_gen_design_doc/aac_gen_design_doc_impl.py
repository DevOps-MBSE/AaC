"""AaC Plugin implementation module for the aac-gen-design-doc plugin."""

import os
import sys
from functools import partial

from iteration_utilities import flatten
from jinja2 import Template, Environment, FileSystemLoader

from aac import parser, util
from aac.template_engine import (
    TemplateOutputFile,
    generate_template,
    load_templates,
    write_generated_templates_to_file,
)

plugin_version = "0.0.1"
default_template_file = "templates/system-design-doc.md.jinja2"


def gen_design_doc(architecture_files: str, output_directory: str, template_file: str):
    """
    Generate a System Design Document from Architecture-as-Code models.

    Args:
        `architecture_files` <str>: A comma-separated list of yaml file(s) containing the modeled
                                      system for which to generate the System Design document.
        `output_directory` <str>: The directory to which the System Design document will be written.
        `template_file` <str>: The name of the template file to use for generating the document. (optional)
    """
    first_arch_file, *other_arch_files = architecture_files.split(",")
    parsed_models = _get_parsed_models([first_arch_file] + other_arch_files)

    loaded_templates = load_templates(__package__)

    template_file = template_file if template_file else default_template_file
    template_file_name = os.path.basename(template_file)

    # TODO: Find a better solution to select between available templates.
    selected_template, *_ = [t for t in loaded_templates if template_file_name == t.name]

    output_filespec = _get_output_filespec(
        first_arch_file, _get_output_file_extension(template_file_name)
    )

    template_properties = _make_template_properties(parsed_models, first_arch_file)
    generated_document = _generate_system_doc(output_filespec, selected_template, template_properties)
    write_generated_templates_to_file([generated_document], output_directory)

    print(f"Wrote system design document to {os.path.join(output_directory, output_filespec)}")


# TODO: We really need this try/except code in a separate function
def _get_parsed_models(architecture_files: list) -> list:
    try:
        return list(map(parser.parse_file, architecture_files))
    except RuntimeError as re:
        model_file, errors = re.args
        errors = "\n  ".join(errors)

        print(f"Failed to validate {model_file}")
        print(f"Failed with errors:\n  {errors}")

        sys.exit("validation error")


def _make_template_properties(parsed_models: dict, arch_file: str) -> dict:
    title = _get_document_title(arch_file)
    models = _get_from_parsed_models(parsed_models, "model")
    usecases = _get_from_parsed_models(parsed_models, "usecase")
    interfaces = _get_from_parsed_models(parsed_models, "data")
    return {"title": title, "models": models, "usecases": usecases, "interfaces": interfaces}


def _get_document_title(arch_file: str) -> str:
    filespec, _ = os.path.splitext(arch_file)
    return os.path.basename(filespec)


def _get_output_filespec(filespec: str, ext: str) -> str:
    return f"{_get_document_title(filespec)}_system_design_document{ext}"


def _get_output_file_extension(template_filespec: str) -> str:
    _, extension = os.path.splitext(template_filespec.replace(".jinja2", ""))
    return extension


def _get_from_parsed_models(parsed_models: dict, aac_type: str) -> list:
    aac_types = [util.get_models_by_type(m, aac_type) for m in parsed_models]
    return list(flatten([m.values() for m in aac_types]))


def _generate_system_doc(output_filespec: str, selected_template: Template, template_properties: dict) -> TemplateOutputFile:
    template = generate_template(selected_template, template_properties)

    template.file_name = output_filespec
    template.overwrite = True  # TODO: double check
    return template
