""" This module provides a common set of templating and generation functions """
from __future__ import annotations

import os

from attr import attrib, attrs, validators
from jinja2 import Environment, PackageLoader, Template


def load_templates(package_name: str) -> list[Template]:
    """
    Load templates from a `templates` directory within a package.

    Args:
        group_dir_name: name of the templates sub-directory to load templates from.

    Returns:
        list of loaded templates
    """

    env = Environment(
        loader=PackageLoader(package_name, "templates"),
        autoescape=True,
    )

    return _load_templates_from_env(env)


def load_default_templates(group_dir_name: str) -> list[Template]:
    """
    Load default templates embedded in the AaC project based on a template group-name.

    Args:
        group_dir_name: name of the templates sub-directory to load templates from.

    Returns:
        list of loaded templates
    """

    env = Environment(
        loader=PackageLoader("aac", f"templates/{group_dir_name}"),
        autoescape=True,
    )

    return _load_templates_from_env(env)


def _load_templates_from_env(env) -> list:
    return list(map(env.get_template, env.list_templates()))


def generate_templates(templates: list[Template], properties: dict[str, str]) -> dict[str, str]:
    """
    Compile a list of Jinja2 Templates with a dict of template properties into a dict of template name to compiled template content.

    Args:
        templates: list of Jinja2 templates to compile.
        properties: Dict of properties to use when compiling the templates
    """
    generated_templates = {}
    for template in templates:
        template_id = template.name
        generated_templates[template_id] = generate_template(template, properties)

    return generated_templates


def generate_template(template: Template, properties: dict[str, str]) -> str:
    """
    Compile a Jinja2 Template object to a string.

    Args:
        template: Jinja2 template to compile.
        properties: Dict of properties to use when compiling the template

    Returns:
        Compiled/Rendered template as a string
    """
    return template.render(properties)


def write_generated_templates_to_file(
    generated_files: list[TemplateOutputFile], output_dir: str
) -> None:
    """
    Write a list of generated files to the target directory.

    Args:
        generated_files: list of generated files to write to the filesystem
        output_dir: the directory to write the generated files to.
    """

    for generated_file in generated_files:
        _write_file(
            output_dir,
            generated_file.file_name,
            generated_file.content,
            generated_file.overwrite,
        )


def _write_file(path: str, file_name: str, content: str, overwrite: bool) -> None:
    """
    Write string content to a file.

    Args:
        path: the path to the directory that the file will be written to
        file_name: the name of the file to be written
        content: contents of the file to write
        overwrite: whether to overwrite an existing file, if false the file will not be altered.
    """
    file_to_write = os.path.join(path, file_name)
    if not overwrite and os.path.exists(file_to_write):
        print(f"{file_to_write} already exists, skipping write")
    else:
        file = open(file_to_write, "w")
        file.writelines(content)
        file.close()


@attrs(slots=True, auto_attribs=True)
class TemplateOutputFile:
    """Class containing all of the relevant information necessary to handle writing templates to files."""

    file_name: str = attrib(validator=validators.instance_of(str))
    content: str = attrib(validator=validators.instance_of(str))
    overwrite: bool = attrib(validator=validators.instance_of(bool))
