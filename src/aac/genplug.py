"""
A plugin to generate new plugins based on a specifically structured AaC model file.

The plugin AaC model must define behaviors using the command BehaviorType.  Each
defined behavior becomes a new command for the aac CLI.
"""
import os

import yaml

from aac import hookimpl, parser, util
from aac.AacCommand import AacCommand, AacCommandArgument
from aac.template_engine import (TemplateOutputFile, generate_templates,
                                 load_default_templates,
                                 write_generated_templates_to_file)


@hookimpl
def get_commands() -> list[AacCommand]:
    """
    Returns the gen-plugin command type to the plugin infrastructure.

    Returns:
        A list of AacCommands
    """
    command_arguments = [
        AacCommandArgument(
            "architecture_file",
            "The yaml file containing the AaC DSL of the plugin architecture.",
        )
    ]

    plugin_commands = [
        AacCommand(
            "gen-plugin",
            "Generates an AaC plugin from an AaC model of the plugin",
            generate_plugin,
            command_arguments,
        )
    ]

    return plugin_commands


@hookimpl
def get_base_model_extensions() -> str:
    """
    Returns the CommandBehaviorType modeling language extension to the plugin infrastructure.

    Returns:
        string representing yaml extensions and data definitions employed by the plugin
    """
    return """
ext:
   name: CommandBehaviorType
   type: BehaviorType
   enumExt:
      add:
         - command
---
ext:
   name: DescriptField
   type: Field
   dataExt:
      add:
        - name: description
          type: string
"""


class GeneratePluginException(Exception):
    """Exceptions specifically concerning plugin generation."""

    pass


def generate_plugin(architecture_file: str) -> None:
    """
    Entrypoint command to generate the plugin.

    Args:
        architecture_file (str): filepath to the architecture file.
    """
    plug_dir = os.path.dirname(os.path.abspath(architecture_file))

    try:
        if _is_user_desired_output_directory(architecture_file, plug_dir):
            parsed_model = parser.parse_file(architecture_file, True)
            templates = list(_compile_templates(parsed_model).values())
            write_generated_templates_to_file(templates, plug_dir)
    except GeneratePluginException as exception:
        print(f"gen-plugin error [{architecture_file}]:  {exception}.")


def _compile_templates(parsed_models: dict[str, dict]) -> dict[str, list[TemplateOutputFile]]:
    """
    Parse the model and generate the plugin template accordingly.

    Args:
        parsed_models: Dict representing the plugin models

    Returns:
        List of TemplateOutputFile objects that contain the compiled templates

    Raises:
        GeneratePluginException: An error encountered during the plugin generation process.
    """

    # Define which templates we want to overwrite.
    templates_to_overwrite = ["plugin.py.jinja2", "setup.py.jinja2"]

    def set_overwrite_value(template: TemplateOutputFile):
        template.overwrite = template.template_name in templates_to_overwrite

    def set_filename_value(template: TemplateOutputFile):
        template.file_name = _convert_template_name_to_file_name(
            template.template_name, plugin_implementation_name
        )

    # ensure model is present and valid, get the plugin name
    plugin_models = util.get_models_by_type(parsed_models, "model")
    if len(plugin_models.keys()) != 1:
        raise GeneratePluginException(
            "Plugin Arch-as-Code yaml must contain one and only one model."
        )

    plugin_model = list(plugin_models.values())[0].get("model")
    plugin_name = plugin_model.get("name")

    # Ensure that the plugin name has that 'aac' package name prepended to it
    if not plugin_name.startswith(__package__):
        plugin_name = f"{__package__}-{plugin_name}"

    plugin_implementation_name = _convert_to_implementation_name(plugin_name)

    # Prepare template variables/properties
    behaviors = util.search(plugin_model, ["behavior"])
    commands = _gather_commands(behaviors)

    plugin = {
        "name": plugin_name,
        "implementation_name": plugin_implementation_name,
    }

    plugin_aac_definitions = [
        _add_definitions_yaml_string(definition)
        for definition in _gather_plugin_aac_definitions(parsed_models)
    ]

    template_properties = {
        "plugin": plugin,
        "commands": commands,
        "aac_definitions": plugin_aac_definitions,
    }
    generated_templates = generate_templates(
        load_default_templates("genplug"), template_properties
    )

    for template in generated_templates.values():
        set_overwrite_value(template)
        set_filename_value(template)

    return generated_templates


def _convert_template_name_to_file_name(template_name: str, plugin_name: str) -> str:
    """
    Convert template names to pythonic file names.

    Args:
        template_name: The template's name
        plugin_name: The plugin's name
    Returns:
        A string containing the personalized/pythonic file name.
    """

    #  we're using that genplug will only ever generate python templates
    assumed_file_extension = ".py"

    #  Strip anything after the .py ending
    strip_index = template_name.index(assumed_file_extension) + len(assumed_file_extension)
    file_name = template_name[:strip_index]

    # Replace "plugin" with the plugin name
    file_name = file_name.replace("plugin", plugin_name)

    return file_name


def _is_user_desired_output_directory(architecture_file: str, output_dir: str) -> bool:
    """
    Ask the user if they're comfortable with the target generation directory.

    Args:
        architecture_file: Name of the architecture file
        output_dir: The path to the target output directory
    Returns:
        boolean True if the user wishes to write to <output_dir>
    """
    first = True
    confirmation = ""
    while confirmation not in ["y", "n", "Y", "N"]:
        if not first:
            print(f"Unrecognized input {confirmation}:  please enter 'y' or 'n'.")
        confirmation = input(
            f"Do you want to generate an AaC plugin in the directory {output_dir}? [y/n]"
        )

    if confirmation in ["n", "N"]:
        print(
            f"Canceled: Please move {architecture_file} to the desired directory and rerun the command."
        )

    return confirmation in ["y", "Y"]


def _gather_commands(behaviors: dict) -> list[dict]:
    """
    Parses the plugin model's behaviors and returns a list of commands derived from the plugin's behavior.

    Args:
        behaviors: The plugin's modeled behaviors
    Returns:
        list of command-type behaviors dicts
    """
    commands = []

    for behavior in behaviors:
        behavior_name = behavior["name"]
        behavior_description = behavior["description"]
        behavior_type = behavior["type"]

        if behavior_type != "command":
            continue

        # First line should end with a period. flake8(D400)
        if not behavior_description.endswith("."):
            behavior_description = f"{behavior_description}."

        behavior["description"] = behavior_description
        behavior["implementation_name"] = _convert_to_implementation_name(behavior_name)
        commands.append(behavior)

    return commands


def _gather_plugin_aac_definitions(parsed_models: dict[str, dict]) -> list[dict]:
    extension_definitions = list(util.get_models_by_type(parsed_models, "ext").values())
    data_definitions = list(util.get_models_by_type(parsed_models, "data").values())
    enum_definitions = list(util.get_models_by_type(parsed_models, "enum").values())

    return extension_definitions + data_definitions + enum_definitions


def _add_definitions_yaml_string(model: dict) -> dict:
    model["yaml"] = yaml.dump(model)
    return model


def _convert_to_implementation_name(original_name: str) -> str:
    return original_name.replace("-", "_")
