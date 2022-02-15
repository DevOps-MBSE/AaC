"""AaC Plugin implementation module for the aac-plantuml plugin."""

# NOTE: It is safe to edit this file.
# This file is only initially generated by the aac gen-plugin, and it won't be overwritten if the file already exists.

import os

from aac import parser, util
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.validator import validation
from aac.template_engine import (
    TemplateOutputFile,
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
        model_types = util.get_models_by_type(models, "model")
        puml_lines = []
        puml_lines.append("@startuml")
        for root_model_name in _find_root_names(model_types):
            model_component_puml = _get_component_content(model_types[root_model_name], [], model_types)
            puml_lines.append(model_component_puml)
        puml_lines.append("@enduml")
        return puml_lines

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
        use_case_types = util.get_models_by_type(models, "usecase")

        participants = []
        sequences = []

        for use_case_title in _find_root_names(use_case_types):

            # declare participants
            usecase_participants = util.search(use_case_types[use_case_title], ["usecase", "participants"])
            for usecase_participant in usecase_participants:  # each participant is a field type
                participants.append({
                    "type": usecase_participant.get("type"),
                    "name": usecase_participant.get("name"),
                })

            # process steps
            steps = util.search(use_case_types[use_case_title], ["usecase", "steps"])
            for step in steps:  # each step of a step type
                sequences.append({
                    "source": step.get("source"),
                    "target": step.get("target"),
                    "action": step.get("action"),
                })

            return {
                "title": use_case_title,
                "participants": participants,
                "sequences": sequences
            }

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
        model_types = util.get_models_by_type(models, "model")

        object_declarations = []
        object_compositions = {}
        for model_name in model_types.keys():
            object_declarations.append(model_name)

            for component in util.search(model_types[model_name], ["model", "components", "type"]):
                if model_name not in object_compositions:
                    object_compositions[model_name] = set()

                object_compositions[model_name].add(component)

        object_hierarchies = []
        for parent in object_compositions:
            for child in object_compositions[parent]:
                object_hierarchies.append({"parent": parent, "child": child})

        return {
            "objects": object_declarations,
            "object_hierarchies": object_hierarchies
        }

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
    with validation(parser.parse_file, architecture_file_path) as result:
        file_name, _ = os.path.splitext(os.path.basename(architecture_file_path))
        generated_file_name = f"{file_name}.puml"

        template_properties = property_generator(result.model)
        generated_templates = generate_templates(
            load_default_templates(f"{plugin_name}/{puml_type}"), template_properties
        )

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
        components = util.search(model, ["model", "components"])
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


def _get_component_content(root, existing, model_types):

    puml_lines = []
    model_name = root["model"]["name"]

    # define UML interface for each input
    inputs = util.search(root, ["model", "behavior", "input"])
    for input in inputs:
        if not input["type"] in existing:
            puml_lines.append("interface {}".format(input["type"]))
            existing.append(input["type"])

    # define UML interface for each output
    outputs = util.search(root, ["model", "behavior", "output"])
    for output in outputs:
        if not output["type"] in existing:
            puml_lines.append("interface {}".format(output["type"]))
            existing.append(output["type"])

    # define UML package for each component
    components = util.search(root, ["model", "components"])

    if len(components) > 0:
        # if the model has a components, show it as a package
        puml_lines.append('package "{}" {{'.format(model_name))
        existing.append(model_name)
        for component in components:
            # component is a Field type
            component_type = component["type"]

            component_puml = _get_component_content(model_types[component_type], existing, model_types)

            puml_lines.append(component_puml)

        puml_lines.append("}")
    else:
        # if there are no components, show it as a class
        inputs = util.search(root, ["model", "behavior", "input"])
        for input in inputs:
            puml_lines.append("{} -> [{}] : {}".format(input["type"], model_name, input["name"]))
        outputs = util.search(root, ["model", "behavior", "output"])
        for output in outputs:
            puml_lines.append("[{}] -> {} : {}".format(model_name, output["type"], output["name"]))

    return "\n".join(puml_lines)
