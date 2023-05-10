"""AaC Plugin implementation module for the Generate Plugin plugin."""

import logging
import yaml

from os import makedirs, path, rename
from typing import Any

from aac import __version__
from aac.io.parser import parse
from aac.lang.constants import (
    DEFINITION_FIELD_COMMANDS,
    DEFINITION_FIELD_DEFINITION_SOURCES,
    DEFINITION_FIELD_DISPLAY,
    DEFINITION_FIELD_GROUP,
    DEFINITION_FIELD_HELP_TEXT,
    DEFINITION_FIELD_INPUT,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_OUTPUT,
    DEFINITION_FIELD_TYPE,
    ROOT_KEY_ENUM,
    ROOT_KEY_EXTENSION,
    ROOT_KEY_PLUGIN,
    ROOT_KEY_SCHEMA,
)
from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.definition import Definition
from aac.plugins import OperationCancelled
from aac.plugins.first_party.gen_plugin.GeneratePluginException import GeneratePluginException
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.templates.engine import (
    TemplateOutputFile,
    generate_templates,
    load_templates,
    write_generated_templates_to_file,
)
from aac.validate import validated_definitions


plugin_name = "Generate Plugin"

PLUGIN_TYPE_FIRST_STRING = "first"
PLUGIN_TYPE_THIRD_STRING = "third"

EXPECTED_FIRST_PARTY_DIRECTORY_PATH = str(path.join("src", "aac", "plugins"))


def generate_plugin(architecture_file: str) -> PluginExecutionResult:
    """
    Entrypoint command to generate the plugin.

    Args:
        architecture_file (str): filepath to the architecture file.
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
    with validated_definitions(_collect_all_plugin_definitions(architecture_file_path)) as validation_result:
        templates: list = list(
            _prepare_and_generate_plugin_files(
                validation_result.definitions, plugin_type, architecture_file_path, plugin_output_directory
            ).values()
        )
        write_generated_templates_to_file(templates)
        return f"Successfully created a {plugin_type}-party plugin in {plugin_output_directory}"


def _collect_all_plugin_definitions(architecture_file_path: str) -> list[Definition]:
    definitions = parse(architecture_file_path)
    plugin, *_ = get_definitions_by_root_key(ROOT_KEY_PLUGIN, definitions)
    definition_sources = plugin.get_top_level_fields().get(DEFINITION_FIELD_DEFINITION_SOURCES, [])
    definition_sources_definitions = [definition for path in definition_sources for definition in parse(path)]
    return definitions + definition_sources_definitions


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
    output_files: dict[str, TemplateOutputFile],
    overwite_files: list[str],
    plugin_implementation_name,
):
    """
    Apply post-generation settings to the files prior to them being written to the filesystem.

    Args:
        output_files (list[TemplateOutputFile]): The generated files to apply the settings to (this mutates output_files).
        overwite_files (list[str]): A list of template files that can be overwritten.
        plugin_implementation_name: The plugin's implementation name.
    """

    def set_overwrite_value(output_file: TemplateOutputFile):
        output_file.overwrite = output_file.template_name in overwite_files

    def set_filename_value(output_file: TemplateOutputFile):
        output_file.file_name = _convert_template_name_to_file_name(output_file.template_name, plugin_implementation_name)

    for output_file in output_files.values():
        set_overwrite_value(output_file)
        set_filename_value(output_file)


def _get_overwriteable_templates() -> list[str]:
    """Returns a manually maintained list of templates that can be overwritten."""
    return ["setup.py.jinja2"]


def _get_template_output_directories(plugin_type: str, architecture_file_path: str, plugin_name: str) -> dict[str, str]:
    """Returns a manually maintained list of templates and their output directories."""

    architecture_file_directory_path = path.dirname(architecture_file_path)

    # First party files are generated at the same level as the architecture file
    first_party_directories = {
        "test_plugin_impl.py.jinja2": path.join("tests", "plugins"),
        "plugin_impl.py.jinja2": architecture_file_directory_path,
        "__init__.py.jinja2": architecture_file_directory_path,
    }

    # Third party files are generated a level below the architecture file
    third_party_directories = {
        "test_plugin_impl.py.jinja2": "tests",
        "README.md.jinja2": "",
        "__init__.py.jinja2": plugin_name,
        "plugin_impl.py.jinja2": plugin_name,
        "setup.py.jinja2": "",
        "tox.ini.jinja2": "",
    }

    return first_party_directories if plugin_type == PLUGIN_TYPE_FIRST_STRING else third_party_directories


def _generate_template_files(
    plugin_type: str, output_directory: str, output_directories: dict, template_properties: dict
) -> dict[str, TemplateOutputFile]:
    """Generates the Jinja2 templates with the template properties."""
    directories = {name: path.join(output_directory, output_file) for name, output_file in output_directories.items()}
    return generate_templates(load_templates(__package__, f"templates/{plugin_type}_party"), directories, template_properties)


def _prepare_and_generate_plugin_files(
    definitions: list[Definition], plugin_type: str, architecture_file_path: str, output_directory: str
) -> dict[str, TemplateOutputFile]:
    """
    Parse the plugin definitions and generate the plugin template accordingly.

    Args:
        definitions (list[Definition]): A list of definitions
        plugin_type (str): A string representing the plugin type {PLUGIN_TYPE_FIRST_STRING, PLUGIN_TYPE_THIRD_STRING}
        architecture_file_path (str): The filepath to the architecture file used to generate the plugin.
        output_directory (str): The directory in which to output the generated plugin files.

    Returns:
        List of TemplateOutputFile objects that contain the compiled templates

    Raises:
        GeneratePluginException: An error encountered during the plugin generation process.
    """
    template_properties = _gather_template_properties(definitions, architecture_file_path, plugin_type)

    plugin_name = template_properties.get(ROOT_KEY_PLUGIN, {}).get(DEFINITION_FIELD_NAME)
    plugin_implementation_name = template_properties.get(ROOT_KEY_PLUGIN, {}).get("implementation_name")
    plugin_implementation_name = _convert_to_implementation_name(plugin_name)

    templates_to_overwrite = _get_overwriteable_templates()
    template_output_directories = _get_template_output_directories(
        plugin_type, architecture_file_path, plugin_implementation_name
    )

    if plugin_type == PLUGIN_TYPE_THIRD_STRING:
        template_properties["aac_version"] = __version__
        new_sources = {}
        definition_sources = {definition.source.uri for definition in definitions}
        for source in definition_sources:
            new_sources[source] = _get_updated_file_path(source, output_directory, plugin_implementation_name)
            _move_architecture_file_to_plugin_root(source, new_sources[source])

        for definition in definitions:
            definition.source.uri = new_sources.get(definition.source.uri)

    generated_templates = _generate_template_files(
        plugin_type, output_directory, template_output_directories, template_properties
    )

    _apply_output_template_properties(generated_templates, templates_to_overwrite, plugin_implementation_name)

    return generated_templates


def _gather_template_properties(
    parsed_definitions: list[Definition], architecture_file_path: str, plugin_type: str
) -> dict[str, Any]:
    """
    Analyzes the models and returns the necessary template data to generate the plugin.

    Args:
        parsed_definitions (list[Definition]): A list of plugin definitions.
        architecture_file_path (str): The filepath to the architecture file used to generate the plugin.
        plugin_type (str): Whether the plugin is first or third party.

    Returns:
        A dictionary of properties to be used when generating the jinja templates.
    """
    plugins = get_definitions_by_root_key(ROOT_KEY_PLUGIN, parsed_definitions)
    if len(plugins) != 1:
        raise GeneratePluginException("Plugin AaC YAML must contain one, and only one, plugin definition.")

    plugin, *_ = plugins
    plugin_implementation_name = _convert_to_implementation_name(plugin.name)

    # Prepare template variables/properties
    commands = _gather_command_properties(plugin)

    plugin = {
        DEFINITION_FIELD_NAME: plugin.name,
        "implementation_name": plugin_implementation_name,
    }

    plugin_aac_definitions = [
        {
            "type": definition.get_root_key(),
            "type_name": definition.name,
            "yaml": definition.to_yaml(),
        } for definition in _gather_plugin_aac_definitions(parsed_definitions)
    ]

    package_name = path.basename(path.dirname(architecture_file_path))
    architecture_file = {
        DEFINITION_FIELD_NAME: path.basename(architecture_file_path),
        "package_name": f"first_party.{package_name}" if plugin_type == PLUGIN_TYPE_FIRST_STRING else package_name,
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
    return template_name.replace(".jinja2", "").replace("plugin", plugin_name.lower())


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


def _gather_command_properties(plugin_definition: Definition) -> list[dict]:
    """
    Parse the plugin definition's commands and return a list of each command's template properties.

    Args:
        plugin_definition (Definition): The plugin definition.

    Returns:
        A list of template property dicts for the plugin's commands.
    """

    def modify_command_input_output_entry(in_out_entry: dict):
        """Modify the input and output entries of a behavior definition to reduce complexity in the templates."""
        python_type = in_out_entry.get("python_type")

        in_out_entry[DEFINITION_FIELD_NAME] = in_out_entry.get(DEFINITION_FIELD_NAME).removeprefix("--")

        if python_type:
            in_out_entry[DEFINITION_FIELD_TYPE] = python_type
            in_out_entry["python_type_default"] = type(python_type)

        return in_out_entry

    commands = []

    for cmd in plugin_definition.get_top_level_fields().get(DEFINITION_FIELD_COMMANDS, []):
        command = {}

        # First line should end with a period. flake8(D400)
        command_help_text = cmd.get(DEFINITION_FIELD_HELP_TEXT)
        if not command_help_text.endswith("."):
            command_help_text = f"{command_help_text}."

        command_input = cmd.get(DEFINITION_FIELD_INPUT)
        if command_input:
            command[DEFINITION_FIELD_INPUT] = [modify_command_input_output_entry(i) for i in command_input]

        command_output = cmd.get(DEFINITION_FIELD_OUTPUT)
        if command_output:
            command[DEFINITION_FIELD_OUTPUT] = [modify_command_input_output_entry(o) for o in command_output]

        command_name = cmd.get(DEFINITION_FIELD_NAME)
        command[DEFINITION_FIELD_NAME] = command_name
        command[DEFINITION_FIELD_HELP_TEXT] = command_help_text
        command[DEFINITION_FIELD_DISPLAY] = cmd.get(DEFINITION_FIELD_NAME, command_name)
        command[DEFINITION_FIELD_GROUP] = cmd.get(DEFINITION_FIELD_GROUP)
        command["implementation_name"] = _convert_to_implementation_name(command_name)
        commands.append(command)

    return commands


def _gather_plugin_aac_definitions(parsed_definitions: list[Definition]) -> list[Definition]:
    """
    Gather all AaC definitions declared by the model.

    Args:
        parsed_definitions (list[Definition]): The list of plugin definitions.

    Returns:
        A list of AaC definitions provided by the plugin
    """
    extension_definitions = get_definitions_by_root_key(ROOT_KEY_EXTENSION, parsed_definitions)
    schema_definitions = get_definitions_by_root_key(ROOT_KEY_SCHEMA, parsed_definitions)
    enum_definitions = get_definitions_by_root_key(ROOT_KEY_ENUM, parsed_definitions)

    return extension_definitions + schema_definitions + enum_definitions


def _add_definitions_yaml_string(structure: dict) -> dict:
    structure["yaml"] = yaml.dump(structure)
    return structure


def _convert_to_implementation_name(original_name: str) -> str:
    """Converts a plugin name to a pythonic version for implementation."""
    return original_name.replace("-", "_").replace(" ", "_").lower()


def _get_repository_root_directory_from_path(system_path: str) -> str:
    """Returns the root of the AaC Repository from a path within the repository's plugins directory."""
    target_index = system_path.find(EXPECTED_FIRST_PARTY_DIRECTORY_PATH)

    if target_index < 0:
        logging.error(f"Failed to find '{EXPECTED_FIRST_PARTY_DIRECTORY_PATH}' in plugin output path: '{system_path}'.")
        raise (
            GeneratePluginException(f"Expected file path '{system_path}' to contain '{EXPECTED_FIRST_PARTY_DIRECTORY_PATH}'.")
        )

    return system_path[:target_index]


def _get_updated_file_path(architecture_file_path: str, output_directory: str, generated_plugin_name: str) -> str:
    """Return the new file path to which the plugin architecture file will be moved."""
    architecture_file_path = path.join(output_directory, architecture_file_path)
    file_name = path.basename(architecture_file_path)
    new_file_path = path.join(output_directory, generated_plugin_name, file_name)
    return new_file_path


def _move_architecture_file_to_plugin_root(architecture_file_path: str, new_file_path: str) -> None:
    """Move the architecture file to the plugin root directory."""
    makedirs(path.dirname(new_file_path), exist_ok=True)
    rename(architecture_file_path, new_file_path)
