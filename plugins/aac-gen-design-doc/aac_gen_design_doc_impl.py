"""AaC Plugin implementation module for the aac-gen-design-doc plugin."""

import os
import sys
from functools import partial

from iteration_utilities import flatten
from markdown_generator import MarkdownDesignDocumentGenerator

from aac import parser, util

plugin_version = "0.0.1"


# TODO: Once we can get lists, fix type hint and docstring type for architecture_files.
def gen_design_doc(architecture_files: str, output_directory: str, template_file: str):
    """
    Generate a System Design Document from Architecture-as-Code models.

    Args:
        `architecture_files` <str>: A comma-separated list of yaml file(s) containing the modeled
                                      system for which to generate the System Design document.
        `output_directory` <str>: The directory to which the System Design document will be written.
        `template_file` <str>: The name of the template file to use for generating the document.
    """
    first_arch_file, *other_arch_files = architecture_files.split(",")
    parsed_models = _get_parsed_models([first_arch_file] + other_arch_files)

    template_properties = {
        "doc_title": ".".join(os.path.basename(first_arch_file).split(".")[:-1]),
        "models": list(
            flatten(
                [m.values() for m in [util.get_models_by_type(m, "model") for m in parsed_models]]
            )
        ),
        "usecases": list(
            flatten(
                [
                    m.values()
                    for m in [util.get_models_by_type(m, "usecase") for m in parsed_models]
                ]
            )
        ),
        "interfaces": list(
            flatten(
                [m.values() for m in [util.get_models_by_type(m, "data") for m in parsed_models]]
            )
        ),
    }

    _maybe_create_directory(output_directory)

    generator = MarkdownDesignDocumentGenerator()
    x = generator.generate_templates(generator.load_templates(), template_properties)
    write = partial(_write_content, output_directory)
    [write(filespec, content) for filespec, content in x.items()]


# TODO: We really need this try/except code in a separate function
def _get_parsed_models(architecture_files: list) -> list:
    models = None
    try:
        models = list(map(parser.parse_file, architecture_files))
    except RuntimeError as re:
        model_file, errors = re.args
        errors = "\n  ".join(errors)

        print(f"Failed to validate {model_file}")
        print(f"Failed with errors:\n  {errors}")

        sys.exit("validation error")

    return models


def _maybe_create_directory(output_directory: str) -> None:
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)


def _write_content(output_directory: str, filespec: str, content: str):
    with open(os.path.join(output_directory, filespec), "w") as f:
        f.write(content)
