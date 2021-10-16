"""
A plugin to generate new plugins based on a specifically structured AaC model file.
The plugin AaC model must define behaviors using the command BehaviorType.  Each
defined behavior becomes a new command for the aac CLI.
"""
import attr
import os
import yaml

from aac import util, hookimpl
from aac.AacCommand import AacCommand
from aac.template_engine import load_templates, generate_templates


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Returns the gen-plugin command type to the plugin infrastructure.
    """
    my_cmd = AacCommand(
        "gen-plugin", "Generates an AaC plugin from an AaC model of the plugin", generate_plugin
    )
    return [my_cmd]


@hookimpl
def get_base_model_extensions() -> str:
    """
    Returns the CommandBehaviorType modeling language extension to the plugin infrastructure.
    """
    return """
ext:
   name: CommandBehaviorType
   type: BehaviorType
   enumExt:
      add:
         - command
"""


class GeneratePluginException(Exception):
    """Exceptions specifically concerning plugin generation."""

    pass


@attr.s
class TemplateOutputFile:
    """Class containing all of the relevant information necessary to handle writing templates to files."""

    file_name = attr.ib()
    template = attr.ib()
    overwrite = attr.ib()


def generate_plugin(arch_file: str, parsed_model: dict) -> None:
    """Entrypoint command to generate the plugin."""
    plug_dir = os.path.dirname(os.path.realpath(arch_file))

    try:
        if is_user_desired_output_directory(arch_file, plug_dir):
            templates = compile_templates(parsed_model)
            write_generated_templates_to_file(templates, plug_dir)
    except GeneratePluginException as exception:
        print(f"gen-plugin error [{arch_file}]:  {exception}.")


def compile_templates(parsed_models: dict[str, dict]) -> list[TemplateOutputFile]:
    """
    Parse the model and generate the plugin template accordingly.

    :return: Dict of file name to the rendered template
    """

    # ensure model is present and valid, get the plugin name
    plugin_models = util.get_models_by_type(parsed_models, "model")
    if len(plugin_models.keys()) != 1:
        raise GeneratePluginException(
            "Plugin Arch-as-Code yaml must contain one and only one model."
        )

    plugin_model = list(plugin_models.values())[0].get("model")
    plugin_name = plugin_model.get("name")
    plugin_implementation_name = get_implementation_name(plugin_name)

    # Ensure that the plugin name has package name prepended to it
    if not plugin_name.startswith(__package__):
        plugin_name = "{__package__}-{plugin_name}"

    behaviors = util.search(plugin_model, ["behavior"])
    commands = gather_commands(behaviors)

    plugin_templates = load_templates("genplug")

    plugin = {
        "name": plugin_model.get("name"),
        "implementation_name": plugin_implementation_name,
    }

    extensions = [
        add_extensions_yaml_string(definition) for definition in gather_extensions(parsed_models)
    ]

    template_properties = {"plugin": plugin, "commands": commands, "extensions": extensions}
    generated_templates = generate_templates(plugin_templates, template_properties)

    # Define which templates we want to overwrite.
    templates_to_overwrite = ["plugin.py.jinja2", "setup.py.jinja2"]

    # Combine the generated templates into a map of file_name: file_contents
    files_to_write = []
    for template_name, template_content in generated_templates.items():
        file_name = convert_template_name_to_file_name(template_name, plugin_implementation_name)
        overwrite = template_name in templates_to_overwrite

        files_to_write.append(TemplateOutputFile(file_name, template_content, overwrite))

    return files_to_write


def write_generated_templates_to_file(templates: list[TemplateOutputFile], plug_dir: str) -> None:
    """ """

    for template_output_file in templates:
        write_file(
            plug_dir,
            template_output_file.file_name,
            template_output_file.overwrite,
            template_output_file.template,
        )


def convert_template_name_to_file_name(template_name: str, plugin_name: str) -> str:
    """ """
    #  we're using that genplug will only ever generate python templates
    assumed_file_extension = ".py"

    #  Strip anything after the .py ending
    strip_index = template_name.index(assumed_file_extension) + len(assumed_file_extension)
    file_name = template_name[:strip_index]

    # Replace "plugin" with the plugin name
    file_name = file_name.replace("plugin", plugin_name)

    return file_name


def is_user_desired_output_directory(arch_file: str, plug_dir: str) -> bool:
    """ """
    first = True
    confirmation = ""
    while confirmation not in ["y", "n", "Y", "N"]:
        if not first:
            print(f"Unrecognized input {confirmation}:  please enter 'y' or 'n'.")
        confirmation = input(
            f"Do you want to generate an AaC plugin in the directory {plug_dir}? [y/n]"
        )

    if confirmation in ["n", "N"]:
        print(f"Canceled: Please move {arch_file} to the desired directory and rerun the command.")

    return confirmation in ["y", "Y"]


def gather_commands(behaviors: dict) -> list[dict]:
    """
    Parses the plugin model's behaviors and returns a list of commands derived from the plugin's behavior.

    :return: list of command yaml dicts
    """
    commands = []

    for behavior in behaviors:
        behavior_name = behavior["name"]
        behavior_description = behavior["description"]
        behavior_type = behavior["type"]

        if behavior_type != "command":
            continue

        if behavior_description.startswith("'"):
            behavior_description = behavior_description[1:]

        if behavior_description.endswith("'"):
            behavior_description = behavior_description[:-1]

        # First line should end with a period. flake8(D400)
        if not behavior_description.endswith("."):
            behavior_description = f"{behavior_description}."

        behavior["description"] = behavior_description
        behavior["implementation_name"] = get_implementation_name(behavior_name)
        commands.append(behavior)

    return commands


def gather_extensions(parsed_models: dict[str, dict]) -> list[dict]:
    """ """
    extension_definitions = list(util.get_models_by_type(parsed_models, "ext").values())
    data_definitions = list(util.get_models_by_type(parsed_models, "data").values())

    return extension_definitions + data_definitions


def add_extensions_yaml_string(extension_model: dict) -> dict:
    extension_model["yaml"] = yaml.dump(extension_model)
    return extension_model


def process_extensions(parsed_models: dict[str, dict]) -> list[str]:
    """
    Extract data and extensions from the plugin model.

    :param: parsed_models - the yaml-parsed plugin models
    :type: dict
    :return: list of extensions and data definitions
    """
    plugin_ext_lines = []

    for model_data in parsed_models.value():
        if (
            "data" in model_data or "ext" in model_data
        ):  # only include data and ext (exclude others)
            plugin_ext_lines.append(yaml.dump(model_data))

    return plugin_ext_lines


def write_file(path: str, file_name: str, overwrite: bool, content: str):
    """
    Write string content to a file.

    :param: path - the path to the directory that the file will be written to
    :type: str
    :param: file_name - the name of the file to be written
    :type: str
    :param: overwrite - whether to overwrite an existing file, if false the file will not be altered.
    :type: bool
    :param: content - contents of the file to write
    :type: str
    """
    file_to_write = os.path.join(path, file_name)
    if not overwrite and os.path.exists(file_to_write):
        print(f"{file_to_write} already exists, skipping write")
    else:
        file = open(file_to_write, "w")
        file.writelines(content)
        file.close()


def get_implementation_name(original_name: str) -> str:
    return original_name.replace("-", "_")
