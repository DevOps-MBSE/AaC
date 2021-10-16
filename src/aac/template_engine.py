""" This module provides a common set of templating and generation functions """
import os

from jinja2 import Template, FileSystemLoader, Environment, PackageLoader


def load_templates(group_dir_name: str) -> list[Template]:
    """ """
    # env = Environment(
    #     loader=PackageLoader(__package__, "templates"),
    #     autoescape=True,
    # )
    path = os.path.realpath(f"{TEMPLATES_DIR_PATH}/{group_dir_name}")

    env = Environment(
        loader=FileSystemLoader(path),
        autoescape=True,
    )

    templates = []
    for template_name in env.list_templates():
        templates.append(env.get_template(template_name))

    return templates


def generate_templates(templates: list[Template], properties: dict[str, str]) -> dict[str, str]:
    """ """
    rendered_tempates = {}

    for template in templates:
        rendered_tempates[template.name] = generate_template(template, properties)

    return rendered_tempates


def generate_template(template: Template, properties: dict[str, str]) -> str:
    """ """

    return template.render(properties)


# Constants
TEMPLATES_DIR_PATH = "src/templates"
