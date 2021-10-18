""" This module provides a common set of templating and generation functions """
import os

from jinja2 import Template, FileSystemLoader, Environment


def load_templates(group_dir_name: str) -> list[Template]:
    """
    Load default templates based on group-name.

    Args:
        group_dir_name: name of the templates sub-directory to load templates from.

    Returns:
        list of loaded templates
    """
    path = os.path.realpath(f"{TEMPLATES_DIR_PATH}/{group_dir_name}")

    # Packageloader returned errors when trying to load templates in the aac package
    #   We may have to resort to a custom loader if Filesystem doesn't work with distributions.
    env = Environment(
        loader=FileSystemLoader(path),
        autoescape=True,
    )

    templates = []
    for template_name in env.list_templates():
        templates.append(env.get_template(template_name))

    return templates


def generate_templates(templates: list[Template], properties: dict[str, str]) -> dict[str, str]:
    """
    Compile a list of Jinja2 Template objects to a list of strings.

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


# Constants
TEMPLATES_DIR_PATH = "src/templates"
