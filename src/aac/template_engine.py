import os
from jinja2 import Template, FileSystemLoader, Environment, PackageLoader

""" This module provides a common set of templating and generation functions """

env = Environment(
    loader=PackageLoader("aac", "templates"),
    autoescape=True,
)


def load_templates(group_dir_name: str) -> list[Template]:

    env = Environment(
        loader=PackageLoader("template_engine", "templates"),
        autoescape=True,
    )

    path = os.path.realpath(f"{TEMPLATES_DIR_PATH}/{group_dir_name}")
    print()
    print(path)
    # loader = FileSystemLoader(path)
    # return loader.list_templates()
    return env.loader.list_templates()


# Constants
TEMPLATES_DIR_PATH = "src/templates"
