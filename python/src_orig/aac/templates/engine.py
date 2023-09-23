"""This module provides a common set of templating and generation functions."""

from __future__ import annotations
import os
from typing import Callable

from attr import attrib, attrs, validators
from jinja2 import Environment, PackageLoader, Template, TemplateError

from aac.io.writer import write_file
from aac.templates.error import AacTemplateError


def load_templates(package_name: str, template_directory: str = "templates") -> list[Template]:
    """
    Load templates from a `templates` directory within a package.

    Args:
        group_dir_name: name of the templates sub-directory to load templates from
        template_directory: the directory within the package containing the templates. Defaults to 'templates'

    Returns:
        list of loaded templates
    """

    def _load_templates_from_env(env) -> list:
        filtered_templates = list(filter(_is_template, env.list_templates()))
        return list(map(env.get_template, filtered_templates))

    env = Environment(
        loader=PackageLoader(package_name, template_directory),
        autoescape=True,
        lstrip_blocks=True,
        trim_blocks=True,
    )

    return _handle_template_error(
        f"The error occurred while loading the templates from '{template_directory}/' for the '{package_name}' package",
        _load_templates_from_env,
        env,
    )


def _is_template(filename: str) -> bool:
    return filename.endswith("jinja2")


def generate_templates(
    templates: list[Template], output_directories: dict[str, str], properties: dict[str, str]
) -> dict[str, TemplateOutputFile]:
    """
    Compile a list of Jinja2 Templates with a dict of template properties into a dict of template name to compiled template content.

    Args:
        templates: list of Jinja2 templates to compile.
        output_directories: The directories in which to generate the files.
        properties: Dict of properties to use when compiling the templates.

    Returns:
        Dict of template names to TemplateOutputFile objects
    """
    generated_templates = {}
    for template in templates:
        template_id = template.name
        generated_templates[template_id] = generate_template(template, output_directories.get(template_id), properties)

    return generated_templates


def generate_templates_as_strings(templates: list[Template], properties: dict[str, str]) -> dict[str, str]:
    """
    Compile a list of Jinja2 Templates with a dict of template properties into a dict of template name to compiled template content.

    Args:
        templates: list of Jinja2 templates to compile.
        properties: Dict of properties to use when compiling the templates

    Returns:
        Dict of template names to template content strings
    """
    generated_templates = {}
    for template in templates:
        template_id = template.name
        generated_templates[template_id] = generate_template_as_string(template, properties)

    return generated_templates


def generate_template(template: Template, output_directory: str, properties: dict[str, str]) -> TemplateOutputFile:
    """
    Compile a Jinja2 Template object to a TemplateOutputFile object.

    Args:
        template (Template): Jinja2 template to compile.
        output_directory (str): The directory in which to generate the gherkin file.
        properties (dict[str, str]): Dict of properties to use when compiling the template.

    Returns:
        Compiled/Rendered template as a TemplateOutputFile object
    """
    return TemplateOutputFile(
        output_directory=output_directory,
        template_name=template.name,
        content=generate_template_as_string(template, properties),
        overwrite=False,
    )


def generate_template_as_string(template: Template, properties: dict[str, str]) -> str:
    """
    Compile a Jinja2 Template object to a string.

    Args:
        template: Jinja2 template to compile.
        properties: Dict of properties to use when compiling the template

    Returns:
        Compiled/Rendered template as a string
    """
    return _handle_template_error(f"The error occurred while rendering {template.filename}", template.render, properties)


def write_generated_templates_to_file(generated_files: list[TemplateOutputFile]) -> None:
    """
    Write a list of generated files to the target directory.

    Args:
        generated_files: list of generated files to write to the filesystem
    """
    for generated_file in generated_files:
        file_uri = os.path.join(generated_file.output_directory, generated_file.file_name)
        write_file(
            file_uri,
            generated_file.content,
            generated_file.overwrite,
        )


def _handle_template_error(error_reason: str, callback: Callable, *args, **kwargs):
    try:
        return callback(*args, **kwargs)
    except TemplateError as template_error:
        error_message = f"{error_reason}\n{template_error}"

        if hasattr(template_error, "filename"):
            error_message = f"{error_reason}\n{os.path.basename(template_error.filename)}:L{template_error.lineno} {template_error.message}"

        raise AacTemplateError(
            f"{template_error.__class__.__name__} occurred running {__package__}.{callback.__name__}:\n{error_message}"
        )


@attrs(slots=True, auto_attribs=True)
class TemplateOutputFile:
    """
    Class containing all of the relevant information necessary to handle writing templates to files.

    Attributes:
        output_directory (str): The directory in which to generate the file.
        template_name (str): The name of the jinja2 template the generated content is based on
        content (str): The generated content
        overwrite (bool): A boolean to indicate if this template output should overwrite any existing files with the same name.

        file_name: This attribute is not exposed in the constructor. It's up to the user to set the filename.
    """

    output_directory: str = attrib(validator=validators.instance_of(str))
    template_name: str = attrib(validator=validators.instance_of(str))
    file_name: str = attrib(validator=validators.instance_of(str), default="", init=False)
    content: str = attrib(validator=validators.instance_of(str))
    overwrite: bool = attrib(validator=validators.instance_of(bool))
