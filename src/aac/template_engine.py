""" This module provides a common set of templating and generation functions """
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
