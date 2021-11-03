"""AaC Plugin implementation module for the aac-gen-design-doc plugin."""

import os
import sys
from functools import partial

from iteration_utilities import flatten
from jinja2 import Environment, FileSystemLoader

from aac import parser, util

plugin_version = "0.0.1"


def gen_design_doc(template_file: str, architecture_files: str, output_directory: str):
    """
    Generate a System Design Document from Architecture-as-Code models.

    Args:
        `template_file` <str>: The name of the template file to use for generating the document.
        `architecture_files` <str>: A comma-separated list of yaml file(s) containing the modeled
                                      system for which to generate the System Design document.
        `output_directory` <str>: The directory to which the System Design document will be written.
    """
    first_arch_file, *other_arch_files = architecture_files.split(",")
    parsed_models = _get_parsed_models([first_arch_file] + other_arch_files)
    template_properties = _make_template_properties(parsed_models, first_arch_file)

    template_file_name = os.path.basename(template_file)
    output_filespec = _get_document_title(template_file)

    _create_directory_if_does_not_exist(output_directory)

    template = __generate_templates([template_file], template_properties)[template_file_name]
    _write_content(output_directory, output_filespec, template)

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
    return {
        "doc_title": _get_document_title(arch_file),
        "models": _get_from_parsed_models(parsed_models, "model"),
        "usecases": _get_from_parsed_models(parsed_models, "usecase"),
        "interfaces": _get_from_parsed_models(parsed_models, "data"),
    }


def _get_document_title(arch_file: str) -> str:
    filespec, *ext = os.path.splitext(arch_file)
    return os.path.basename(filespec)


def _get_from_parsed_models(parsed_models: dict, aac_type: str) -> list:
    aac_types = [util.get_models_by_type(m, aac_type) for m in parsed_models]
    return list(flatten([m.values() for m in aac_types]))


def _create_directory_if_does_not_exist(output_directory: str) -> None:
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)


def _write_content(output_directory: str, filespec: str, content: str):
    with open(os.path.join(output_directory, filespec), "w") as f:
        f.write(content)


def __generate_templates(templates: list, properties: dict) -> dict:
    """TEMPORARY: Generate all plugin templates.

    TODO: Remove once Alex's template engine changes are in.
    """
    env = Environment(
        loader=FileSystemLoader(f"{os.path.dirname(__file__)}/templates"),
        autoescape=True,
    )

    generated_templates = {}

    for template in [env.get_template(template) for template in env.list_templates()]:
        generated_templates[template.name] = template.render(properties)

    return generated_templates
