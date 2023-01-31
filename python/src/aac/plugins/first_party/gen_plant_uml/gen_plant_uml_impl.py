"""AaC Plugin implementation module for the aac-plantuml plugin."""

import os
from typing import Callable

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.search import search_definition
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.validate import validated_source
from aac.templates.engine import generate_templates, load_templates, write_generated_templates_to_file

plugin_name = "gen-plant-uml"
PLANT_UML_FILE_EXTENSION = ".puml"
COMPONENT_STRING = "component"
OBJECT_STRING = "object"
SEQUENCE_STRING = "sequence"
FILE_NAME_CHARACTERS_TO_REPLACE = ".!@#$%^&*();,\\/?[]{}`~|'"


def puml_component(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Convert an AaC model to Plant UML component diagram.

    Args:
        architecture_file (str): Path to a yaml file containing an AaC usecase from which to generate a Plant UML component diagram.
        output_directory (str): Output directory for the PlantUML (.puml) diagram file.
    """
    architecture_file_path = os.path.abspath(architecture_file)

    def generate_component_diagram(definitions: list[Definition]):
        model_definitions = get_definitions_by_root_key("model", definitions)

        models = []
        for model_definition in model_definitions:
            root_model_name = model_definition.name
            model_properties = _get_model_content(model_definition, set())
            aac_file_name = _extract_aac_file_name(architecture_file)
            generated_file_name = _get_generated_file_name(aac_file_name, COMPONENT_STRING, root_model_name, output_directory)
            models.append(
                {
                    "filename": generated_file_name,
                    "title": model_definition.name,
                    "models": [model_properties],
                }
            )

        return models

    with plugin_result(
        plugin_name,
        _generate_diagram_to_file,
        architecture_file_path,
        output_directory,
        COMPONENT_STRING,
        generate_component_diagram,
    ) as result:
        return result


def puml_sequence(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Convert an AaC usecase to Plant ULM sequence diagram.

    Args:
        architecture_file: str: Path to a yaml file containing an AaC usecase from which to generate a Plant UML sequence diagram.
        output_directory (str): Output directory for the PlantUML (.puml) diagram file (optional)
    """
    architecture_file_path = os.path.abspath(architecture_file)

    def generate_sequence_diagram(definitions: list[Definition]):
        usecase_definitions = get_definitions_by_root_key("usecase", definitions)

        properties = []

        for usecase_definition in usecase_definitions:
            participants = []
            sequences = []

            use_case_title = usecase_definition.name
            # declare participants
            usecase_participants = search_definition(usecase_definition, ["usecase", "participants"])
            for usecase_participant in usecase_participants:  # each participant is a field type
                participants.append(
                    {
                        "type": usecase_participant.get("type"),
                        "name": usecase_participant.get("name"),
                    }
                )

            # process steps
            steps = search_definition(usecase_definition, ["usecase", "steps"])
            for step in steps:  # each step of a step type
                sequences.append(
                    {
                        "source": step.get("source"),
                        "target": step.get("target"),
                        "action": step.get("action"),
                    }
                )

            aac_file_name = _extract_aac_file_name(architecture_file)
            properties.append(
                {
                    "filename": _get_generated_file_name(aac_file_name, SEQUENCE_STRING, use_case_title, output_directory),
                    "title": use_case_title,
                    "participants": participants,
                    "sequences": sequences,
                }
            )

        return properties

    with plugin_result(
        plugin_name,
        _generate_diagram_to_file,
        architecture_file_path,
        output_directory,
        SEQUENCE_STRING,
        generate_sequence_diagram,
    ) as result:
        return result


def puml_object(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Convert an AaC model to Plant ULM object diagram.

    Args:
        architecture_file: str: Path to a yaml file containing an AaC usecase from which to generate a Plant UML object diagram.
        output_directory (str): Output directory for the PlantUML (.puml) diagram file (optional)
    """
    architecture_file_path = os.path.abspath(architecture_file)

    def generate_object_diagram(definitions: list[Definition]):
        model_definitions = get_definitions_by_root_key("model", definitions)

        object_declarations = []
        object_compositions = {}
        for model_definition in model_definitions:
            model_name = model_definition.name
            object_declarations.append(model_name)

            for component in search_definition(model_definition, ["model", "components", "type"]):
                if model_name not in object_compositions:
                    object_compositions[model_name] = set()

                object_compositions.get(model_name, set()).add(component)

        object_hierarchies = []
        for parent in object_compositions:
            for child in object_compositions.get(parent, {}):
                object_hierarchies.append({"parent": parent, "child": child})

        aac_file_name = _extract_aac_file_name(architecture_file)
        return [
            {
                "filename": _get_generated_file_name(aac_file_name, OBJECT_STRING, aac_file_name, output_directory),
                "objects": object_declarations,
                "object_hierarchies": object_hierarchies,
            }
        ]

    with plugin_result(
        plugin_name,
        _generate_diagram_to_file,
        architecture_file_path,
        output_directory,
        OBJECT_STRING,
        generate_object_diagram,
    ) as result:
        return result


def _generate_diagram_to_file(
    architecture_file_path: str, output_directory: str, puml_type: str, property_generator: Callable
) -> str:
    """
    Generic plant UML generate diagram to output handler. Takes a function reference that generates an array of file lines to write to file.

    Args:
        architecture_file_path (str): The path to the architecture as code file.
        output_directory (str): The path to the generated output directory.
        puml_type (str): The name of diagram type. Will be used in the result message.
        property_generator (callable): The diagram-specific template property generation function. Must return a dictionary
                                        of template properties for use with its associated template.

    Returns:
        Result message string
    """
    with validated_source(architecture_file_path) as result:
        get_active_context().add_definitions_to_context(result.definitions)
        full_output_path = os.path.join(output_directory, puml_type)
        output_directories = {f"{puml_type}_diagram.puml.jinja2": full_output_path}
        template_properties = property_generator(result.definitions)
        templates = [
            (
                props.get("filename"),
                generate_templates(load_templates(__package__, f"templates/{puml_type}"), output_directories, props),
            )
            for props in template_properties
        ]

        generated_templates = []
        for (generated_filename, generated_template) in templates:
            _, filename = os.path.split(generated_filename)
            generated_template, *_ = generated_template.values()
            generated_template.file_name = filename
            generated_templates.append(generated_template)

        if output_directory:
            write_generated_templates_to_file(generated_templates)
            return f"Wrote PUML {puml_type} diagram(s) to {full_output_path}."
        else:
            messages = []
            for generated_template in generated_templates:
                messages.append(f"File: {architecture_file_path}\n{generated_template.content}\n")
            return "\n".join(messages)


def _get_model_content(model: Definition, defined_interfaces: set) -> dict:
    """Return content from the specific model relevant to creating a PlantUML diagram.

    Args:
        model (Definition): The model definition from which to extract the needed properties.
        defined_interfaces (set): A collection of inputs and outputs for the model.

    Returns:
        A dictionary containing the model's name, interfaces, components, inputs, and outputs.
    """
    active_context = get_active_context()
    model_name = model.name
    model_interfaces = set()

    # define UML interface for each input
    inputs = search_definition(model, ["model", "behavior", "input"])
    model_inputs = []
    for input in inputs:
        input_name = input.get("name")
        input_type = input.get("type")
        model_inputs.append({"name": input_name, "type": input_type, "target": model_name})

        if input_type not in defined_interfaces:
            defined_interfaces.add(input_type)
            model_interfaces.add(input_type)

    # define UML interface for each output
    outputs = search_definition(model, ["model", "behavior", "output"])
    model_outputs = []
    for output in outputs:
        output_name = output.get("name")
        output_type = output.get("type")
        model_outputs.append({"name": output_name, "type": output_type, "source": model_name})

        if output_type not in defined_interfaces:
            defined_interfaces.add(output_type)
            model_interfaces.add(output_type)

    # define UML package for each component
    components = search_definition(model, ["model", "components"])
    model_components = []

    for component in components:
        component_type = component.get("type")
        model_components.append(_get_model_content(active_context.get_definition_by_name(component_type), defined_interfaces))

    return {
        "name": model_name,
        "interfaces": model_interfaces,
        "components": model_components,
        "inputs": model_inputs,
        "outputs": model_outputs,
    }


def _get_generated_file_name(architecture_file_name: str, puml_type: str, definition_name: str, output_directory: str) -> str:
    """Return the generated file name for the specified definition in the architecture file.

    Args:
        architecture_file_name (str): The AaC filename sans extension.
        puml_type (str): The type of PlantUML diagram to create.
        definition_name (str): The name of the AaC definition.
        output_directory (str): The directory in which to generate the PlantUML diagram.

    Returns:
        The file name into which the generated PlantUML diagram(s) should be generated for the
        provided definition.
    """
    file_name = architecture_file_name.lower()
    definition_name = definition_name.lower()
    return os.path.join(
        output_directory or "",
        puml_type,
        f"{file_name}_{_get_formatted_definition_name(definition_name)}{PLANT_UML_FILE_EXTENSION}",
    )


def _get_formatted_definition_name(definition_name: str) -> str:
    """Format the definition name such that it can be included as part of a file name.

    Args:
        definition_name (str): The name of the definition to be formatted.

    Returns:
        A formatted version of definition name that can be included in
    """
    name = definition_name.strip().lower().replace(" ", "_")
    for char in FILE_NAME_CHARACTERS_TO_REPLACE:
        name = name.replace(char, "")
    return name


def _extract_aac_file_name(architecture_file: str) -> str:
    """Return the filename sans extension and path from the architecture file."""
    aac_file_name, _ = os.path.splitext(os.path.basename(architecture_file))
    return aac_file_name
