"""
A plugin to generate new plugins based on a specifically structured AaC model file.

The plugin AaC model must define behaviors using the command BehaviorType.  Each
defined behavior becomes a new command for the aac CLI.
"""
import logging
import yaml

from os import path

from aac import parser, util
from aac.template_engine import (
    TemplateOutputFile,
    generate_templates,
    load_default_templates,
    write_generated_templates_to_file,
)
from aac.plugins import OperationCancelled
from aac.plugins.gen_plugin.GeneratePluginException import GeneratePluginException
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.validator import validation

plugin_name = "gen-plugin"

PLUGIN_TYPE_FIRST_STRING = "first"
PLUGIN_TYPE_THIRD_STRING = "third"

EXPECTED_FIRST_PARTY_DIRECTORY_PATH = str(path.join("src", "aac", "plugins"))


def generate_plugin(architecture_file: str) -> PluginExecutionResult:
    """
    Entrypoint command to generate the plugin.

    Args:
        architecture_file (str): filepath to the architecture file.
        plugin_type (str): denotes whether to generate a first or third party plugin. If you're not
                            contributing to the AaC repository, then use the option "third".
                            Valid values are: "first", "third"
    """
    architecture_file_path = path.abspath(architecture_file)

    def _generate_plugin():
        plugin_output_directory = path.dirname(architecture_file_path)
        plugin_type = PLUGIN_TYPE_THIRD_STRING

        if _is_plugin_in_aac_repository(architecture_file_path):

            # For first-party plugins, set the path to the repository's root
            plugin_output_directory = _get_repository_root_directory_from_path(architecture_file_path)
            plugin_type = PLUGIN_TYPE_FIRST_STRING

        if _is_user_desired_output_directory(architecture_file_path):
            return _generate_plugin_files_to_directory(architecture_file_path, plugin_output_directory, plugin_type)

        raise OperationCancelled(f"Move {architecture_file_path} to the desired directory and retry.")

    with plugin_result(plugin_name, _generate_plugin) as result:
        return result


def _generate_plugin_files_to_directory(architecture_file_path: str, plugin_output_directory: str, plugin_type: str) -> str:
    with validation(parser.parse_file, architecture_file_path) as validation_result:
        templates = list(
            _prepare_and_generate_plugin_files(validation_result.model, plugin_type, architecture_file_path).values()
        )
        write_generated_templates_to_file(templates, plugin_output_directory)
        return f"Successfully created a {plugin_type}-party plugin in {plugin_output_directory}"


def _is_plugin_in_aac_repository(architecture_file_path: str) -> bool:
    """
    Returns true if the architecture file path is inside the AaC repository.

    Performs a basic check against the file path of the architecture as code plugin file
        to determine if the file's path matches  some partial structure that matches
        the directory hierarchy of the project.

    Args:
        architecture_file_path: str the full path to the architecture file and output directory
    """
    return EXPECTED_FIRST_PARTY_DIRECTORY_PATH in architecture_file_path


def _apply_output_template_properties(
    output_files: list[TemplateOutputFile],
    overwite_files: list[str],
    parent_directories: dict[str, str],
    plugin_implementation_name,
):
    """
    Apply post-generation settings to the files prior to them being written to the filesystem.

    Args:
        output_files (list[TemplateOutputFile]): The generated files to apply the settings to (this mutates output_files)
        overwite_files (list[str]): A list of template files that can be overwritten
        parent_directories (dict[str, str]): A dictionary of directories to generate the output files under
        plugin_implementation_name: The plugin's implementation name
    """

    def set_overwrite_value(output_file: TemplateOutputFile):
        output_file.overwrite = output_file.template_name in overwite_files

    def set_filename_value(output_file: TemplateOutputFile):
        output_file.file_name = _convert_template_name_to_file_name(output_file.template_name, plugin_implementation_name)

    def set_parent_directory_value(output_file: TemplateOutputFile):
        output_file.parent_dir = parent_directories.get(output_file.template_name) or output_file.parent_dir

    for output_file in output_files.values():
        set_overwrite_value(output_file)
        set_filename_value(output_file)
        set_parent_directory_value(output_file)


def _get_overwriteable_templates() -> list[str]:
    """Returns a manually maintained list of templates that can be overwritten."""
    return ["setup.py.jinja2"]


def _get_template_parent_directories(plugin_type: str, architecture_file_path: str, plugin_name: str) -> dict[str, str]:
    """Returns a manually maintained list of templates and their parent directories."""

    architecture_file_directory_path = path.dirname(architecture_file_path)

    # First party files are generated at the same level as the architecture file
    first_party_directories = {
        "test_plugin_impl.py.jinja2": "tests/plugins/",
        "plugin_impl.py.jinja2": architecture_file_directory_path,
        "__init__.py.jinja2": architecture_file_directory_path,
    }

    # Third party files are generated a level belowthe architecture file
    third_party_directories = {
        "plugin_impl.py.jinja2": plugin_name,
        "__init__.py.jinja2": plugin_name,
        "test_plugin_impl.py.jinja2": "tests",
    }

    return first_party_directories if plugin_type == PLUGIN_TYPE_FIRST_STRING else third_party_directories


def _generate_template_files(plugin_type: str, template_properties: dict) -> dict[str, TemplateOutputFile]:
    """Generates the Jinja2 templates with the template properties."""
    template_directory_name = f"genplug/{plugin_type}_party"
    return generate_templates(load_default_templates(template_directory_name), template_properties)


def _prepare_and_generate_plugin_files(
    parsed_models: dict[str, dict], plugin_type: str, architecture_file_path: str
) -> dict[str, list[TemplateOutputFile]]:
    """
    Parse the model and generate the plugin template accordingly.

    Args:
        parsed_models (dict[str, dict]): Dict representing the plugin models
        plugin_type (str): A string representing the plugin type {PLUGIN_TYPE_FIRST_STRING, PLUGIN_TYPE_THIRD_STRING}
        architecture_file_path (str): The filepath to the architecture file used to generate the plugin

    Returns:
        List of TemplateOutputFile objects that contain the compiled templates

    Raises:
        GeneratePluginException: An error encountered during the plugin generation process.
    """
    template_properties = _gather_template_properties(parsed_models, architecture_file_path)

    plugin_name = template_properties.get("plugin").get("name")
    plugin_implementation_name = template_properties.get("plugin").get("implementation_name")

    plugin_implementation_name = _convert_to_implementation_name(plugin_name)
    templates_to_overwrite = _get_overwriteable_templates()
    template_parent_directories = _get_template_parent_directories(
        plugin_type, architecture_file_path, plugin_implementation_name
    )

    generated_templates = _generate_template_files(plugin_type, template_properties)

    _apply_output_template_properties(
        generated_templates,
        templates_to_overwrite,
        template_parent_directories,
        plugin_implementation_name,
    )

    return generated_templates


def _gather_template_properties(parsed_models: dict[str, dict], architecture_file_path: str) -> dict[str, any]:
    """
    Analyzes the models and returns the necessary template data to generate the plugin.

    Args:
        parsed_models (dict[str, dict]): Dict representing the plugin models
        architecture_file_path (str): The filepath to the architecture file used to generate the plugin

    Returns:
        A dictionary of properties to be used when generating the jinja templates.
    """

    # Ensure model is present and valid, get the plugin name
    plugin_models = util.get_models_by_type(parsed_models, "model")
    if len(plugin_models.keys()) != 1:
        raise GeneratePluginException("Plugin Arch-as-Code yaml must contain one and only one model.")

    plugin_model = list(plugin_models.values())[0].get("model")
    plugin_name = plugin_model.get("name")
    plugin_implementation_name = _convert_to_implementation_name(plugin_name)

    # Prepare template variables/properties
    behaviors = util.search(plugin_model, ["behavior"])
    commands = _gather_commands(behaviors)

    plugin = {
        "name": plugin_name,
        "implementation_name": plugin_implementation_name,
    }

    plugin_aac_definitions = [
        _add_definitions_yaml_string(definition) for definition in _gather_plugin_aac_definitions(parsed_models)
    ]

    architecture_file = {
        "name": path.basename(architecture_file_path),
        "parent_directory_name": path.basename(path.dirname(architecture_file_path)),
    }

    template_properties = {
        "plugin": plugin,
        "commands": commands,
        "plugin_definitions": plugin_aac_definitions,
        "architecture_file": architecture_file,
    }

    return template_properties


def _convert_template_name_to_file_name(template_name: str, plugin_name: str) -> str:
    """
    Convert template names to pythonic file names.

    Args:
        template_name (str): The template's name
        plugin_name (str): The plugin's name

    Returns:
        A string containing the customized/pythonic file name.
    """
    return template_name.replace(".jinja2", "").replace("plugin", plugin_name)


def _is_user_desired_output_directory(architecture_file_path: str) -> bool:
    """
    Confirms with the user that they're comfortable with the target generation directory.

    Args:
        architecture_file_path (str): Path to the plugin's architecture file

    Returns:
        boolean True if the user wishes to write to <output_dir>
    """
    output_dir = path.dirname(architecture_file_path)

    first = True
    confirmation = ""
    while confirmation not in ["y", "n", "Y", "N"]:
        if not first:
            print(f"Unrecognized input {confirmation}:  please enter 'y' or 'n'.")
        else:
            first = False

        confirmation = input(f"Do you want to generate an AaC plugin in the directory {output_dir}/? [y/n]")

    return confirmation in ["y", "Y"]


def _gather_commands(behaviors: dict) -> list[dict]:
    """
    Parse the plugin model's behaviors and return a list of commands derived from the plugin's behavior.

    Args:
        behaviors: The plugin's modeled behaviors

    Returns:
        list of command-type behaviors dicts
    """

    def modify_command_input_output_entry(in_out_entry: dict):
        """Modify the input and output entries of a behavior definition to reduce complexity in the templates."""
        python_type = in_out_entry.get("python_type")

        if python_type:
            in_out_entry["type"] = python_type
            in_out_entry["python_type_default"] = type(python_type)

        return in_out_entry

    commands = []

    for behavior in behaviors:
        behavior_name = behavior["name"]
        behavior_description = behavior["description"]
        behavior_type = behavior.get("type")

        if behavior_type != "command":
            continue

        # First line should end with a period. flake8(D400)
        if not behavior_description.endswith("."):
            behavior_description = f"{behavior_description}."

        if behavior.get("input"):
            behavior["input"] = list(map(modify_command_input_output_entry, behavior.get("input")))

        behavior["description"] = behavior_description
        behavior["implementation_name"] = _convert_to_implementation_name(behavior_name)
        commands.append(behavior)

    return commands


def _gather_plugin_aac_definitions(parsed_models: dict[str, dict]) -> list[dict]:
    """
    Gather all AaC definitions declared by the model.

    Args:
        parsed_models (dict[str, dict]): Dict representing the plugin models

    Returns:
        A list of AaC definitions provided by the plugin
    """
    extension_definitions = list(util.get_models_by_type(parsed_models, "ext").values())
    data_definitions = list(util.get_models_by_type(parsed_models, "data").values())
    enum_definitions = list(util.get_models_by_type(parsed_models, "enum").values())

    return extension_definitions + data_definitions + enum_definitions


def _add_definitions_yaml_string(model: dict) -> dict:
    model["yaml"] = yaml.dump(model)
    return model


def _convert_to_implementation_name(original_name: str) -> str:
    """Converts a plugin name to a pythonic version for implementaiton."""
    return original_name.replace("-", "_")


def _get_repository_root_directory_from_path(system_path: str) -> str:
    """Returns the root of the AaC Repository from a path within the repository's plugins directory."""
    target_index = system_path.find(EXPECTED_FIRST_PARTY_DIRECTORY_PATH)

    if target_index < 0:
        logging.error(f"Failed to find '{EXPECTED_FIRST_PARTY_DIRECTORY_PATH}' in plugin output path: '{system_path}'.")
        raise (
            GeneratePluginException(f"Expected file path '{system_path}' to contain '{EXPECTED_FIRST_PARTY_DIRECTORY_PATH}'.")
        )

    return system_path[:target_index]
