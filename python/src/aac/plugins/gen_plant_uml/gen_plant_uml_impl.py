"""AaC Plugin implementation module for the aac-plantuml plugin."""

# NOTE: It is safe to edit this file.
# This file is only initially generated by the aac gen-plugin, and it won't be overwritten if the file already exists.

import os

from aac import parser
from aac.lang.definition_helpers import get_models_by_type, search, convert_parsed_definitions_to_dict_definition
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.validator import validation
from aac.template_engine import (
    generate_templates,
    load_default_templates,
    write_generated_templates_to_file,
)

plugin_name = "gen_plant_uml"
PLANT_UML_FILE_EXTENSION = ".puml"
COMPONENT_STRING = "component"
OBJECT_STRING = "object"
SEQUENCE_STRING = "sequence"


def puml_component(architecture_file: str, output_directory: str = None) -> PluginExecutionResult:
    """
    Convert an AaC model to Plant UML component diagram.

    Args:
        architecture_file: str: Path to a yaml file containing an AaC usecase from which to generate a Plant UML component diagram.
        output_directory (str): Output directory for the PlantUML (.puml) diagram file (optional)
    """
    architecture_file_path = os.path.abspath(architecture_file)

    def generate_component_diagram(models: dict):
        model_types = get_models_by_type(models, "model")

        models = []
        for root_model_name in _find_root_names(model_types):
            model_properties = _get_model_content(model_types[root_model_name], model_types, set())
            models.append(model_properties)

        return {"models": models}

    with plugin_result(
        plugin_name,
        _generate_diagram_to_file,
        architecture_file_path,
        output_directory,
        COMPONENT_STRING,
        generate_component_diagram,
    ) as result:
        return result


def puml_sequence(architecture_file: str, output_directory: str = None) -> PluginExecutionResult:
    """
    Convert an AaC usecase to Plant ULM sequence diagram.

    Args:
        architecture_file: str: Path to a yaml file containing an AaC usecase from which to generate a Plant UML sequence diagram.
        output_directory (str): Output directory for the PlantUML (.puml) diagram file (optional)
    """
    architecture_file_path = os.path.abspath(architecture_file)

    def generate_sequence_diagram(models: dict):
        use_case_types = get_models_by_type(models, "usecase")

        participants = []
        sequences = []

        for use_case_title in _find_root_names(use_case_types):

            # declare participants
            usecase_participants = search(use_case_types[use_case_title], ["usecase", "participants"])
            for usecase_participant in usecase_participants:  # each participant is a field type
                participants.append(
                    {
                        "type": usecase_participant.get("type"),
                        "name": usecase_participant.get("name"),
                    }
                )

            # process steps
            steps = search(use_case_types[use_case_title], ["usecase", "steps"])
            for step in steps:  # each step of a step type
                sequences.append(
                    {
                        "source": step.get("source"),
                        "target": step.get("target"),
                        "action": step.get("action"),
                    }
                )

            return {"title": use_case_title, "participants": participants, "sequences": sequences}

    with plugin_result(
        plugin_name,
        _generate_diagram_to_file,
        architecture_file_path,
        output_directory,
        SEQUENCE_STRING,
        generate_sequence_diagram,
    ) as result:
        return result


def puml_object(architecture_file: str, output_directory: str = None) -> PluginExecutionResult:
    """
    Convert an AaC model to Plant ULM object diagram.

    Args:
        architecture_file: str: Path to a yaml file containing an AaC usecase from which to generate a Plant UML object diagram.
        output_directory (str): Output directory for the PlantUML (.puml) diagram file (optional)
    """
    architecture_file_path = os.path.abspath(architecture_file)

    def generate_object_diagram(models: dict):
        model_types = get_models_by_type(models, "model")

        object_declarations = []
        object_compositions = {}
        for model_name in model_types.keys():
            object_declarations.append(model_name)

            for component in search(model_types[model_name], ["model", "components", "type"]):
                if model_name not in object_compositions:
                    object_compositions[model_name] = set()

                object_compositions[model_name].add(component)

        object_hierarchies = []
        for parent in object_compositions:
            for child in object_compositions[parent]:
                object_hierarchies.append({"parent": parent, "child": child})

        return {"objects": object_declarations, "object_hierarchies": object_hierarchies}

    with plugin_result(
        plugin_name,
        _generate_diagram_to_file,
        architecture_file_path,
        output_directory,
        OBJECT_STRING,
        generate_object_diagram
    ) as result:
        return result


def _generate_diagram_to_file(
    architecture_file_path: str, output_directory: str, puml_type: str, property_generator: callable
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
    with validation(parser.parse, architecture_file_path) as result:
        file_name, _ = os.path.splitext(os.path.basename(architecture_file_path))
        generated_file_name = f"{file_name}_{puml_type}.puml"

        definitions_as_dict = convert_parsed_definitions_to_dict_definition(result.parsed_definitions)
        template_properties = property_generator(definitions_as_dict)
        generated_templates = generate_templates(load_default_templates(f"{plugin_name}/{puml_type}"), template_properties)

        for generated_template in generated_templates.values():
            generated_template.file_name = generated_file_name

        if output_directory:
            write_generated_templates_to_file(list(generated_templates.values()), output_directory)
            return f"Wrote PUML {puml_type} diagram to {generated_file_name}."

        else:
            # Assuming we maintain one template to diagram type
            generated_template = list(generated_templates.values()).pop()
            return f"File: {architecture_file_path}\n{generated_template.content}\n"


def _find_root_names(models) -> list[str]:
    model_names = list(models.keys())

    if len(model_names) == 1:
        return model_names

    # there are multiple models, so we have to look through them
    subcomponents = []  # names of subcomponent models
    for name in model_names:
        model = models[name]
        components = search(model, ["model", "components"])
        for component in components:
            # component is a Field type
            component_type = component["type"]
            # make sure this is a model type (not a data type)
            if component_type in model_names:
                # add the component type to the list of subs
                subcomponents.append(component_type)

    # remove the subs types from model names
    sanitized_model_names = [name for name in model_names if name not in subcomponents]
    return sanitized_model_names


def _get_model_content(model: dict, model_types, defined_interfaces: set):

    model_name = model["model"]["name"]
    model_interfaces = set()

    # define UML interface for each input
    inputs = search(model, ["model", "behavior", "input"])
    model_inputs = []
    for input in inputs:
        input_name = input["name"]
        input_type = input["type"]
        model_inputs.append({"name": input_name, "type": input_type, "target": model_name})

        if input_type not in defined_interfaces:
            defined_interfaces.add(input_type)
            model_interfaces.add(input_type)

    # define UML interface for each output
    outputs = search(model, ["model", "behavior", "output"])
    model_outputs = []
    for output in outputs:
        output_name = output["name"]
        output_type = output["type"]
        model_outputs.append({"name": output_name, "type": output_type, "source": model_name})

        if output_type not in defined_interfaces:
            defined_interfaces.add(output_type)
            model_interfaces.add(output_type)

    # define UML package for each component
    components = search(model, ["model", "components"])
    model_components = []

    for component in components:
        component_type = component["type"]
        model_components.append(_get_model_content(model_types[component_type], model_types, set()))

    return {
        "name": model_name,
        "interfaces": model_interfaces,
        "components": model_components,
        "inputs": model_inputs,
        "outputs": model_outputs,
    }
