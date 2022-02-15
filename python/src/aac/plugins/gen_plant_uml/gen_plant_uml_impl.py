"""AaC Plugin implementation module for the aac-plantuml plugin."""

# NOTE: It is safe to edit this file.
# This file is only initially generated by the aac gen-plugin, and it won't be overwritten if the file already exists.

import os

from aac import parser, util
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.validator import validation

plugin_name = "gen_plant_uml"
PLANT_UML_FILE_EXTENSION = ".puml"


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
        "component",
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

        puml_lines = []

        for use_case_title in _find_root_names(use_case_types):
            puml_lines.append("@startuml")
            puml_lines.append(f"title {use_case_title}")

            # declare participants
            participants = util.search(use_case_types[use_case_title], ["usecase", "participants"])
            for participant in participants:  # each participant is a field type
                participant_type = participant.get("type")
                participant_name = participant.get("name")
                puml_lines.append(f"participant {participant_type} as {participant_name}")

            # process steps
            steps = util.search(use_case_types[use_case_title], ["usecase", "steps"])
            for step in steps:  # each step of a step type
                step_source = step.get("source")
                step_target = step.get("target")
                step_action = step.get("action")
                puml_lines.append(f"{step_source} -> {step_target} : {step_action}")

            puml_lines.append("@enduml")
            return puml_lines

    with plugin_result(
        plugin_name, _generate_diagram_to_file, architecture_file_path, output_directory, "sequence", generate_sequence_diagram
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

        puml_lines = []
        puml_lines.append("@startuml")
        for obj in object_declarations:
            puml_lines.append(f"object {obj}")

        for parent in object_compositions:
            for child in object_compositions[parent]:
                puml_lines.append(f"{parent} *-- {child}")

        puml_lines.append("@enduml")
        return puml_lines

    with plugin_result(
        plugin_name, _generate_diagram_to_file, architecture_file_path, output_directory, "object", generate_object_diagram
    ) as result:
        return result


def _generate_diagram_to_file(
    architecture_file_path: str, output_directory: str, puml_type: str, puml_content_function: callable
) -> str:
    """
    Generic plant UML generate diagram to output handler. Takes a function reference that generates an array of file lines to write to file.

    Args:
        architecture_file_path (str): The path to the architecture as code file.
        output_directory (str): The path to the generated output directory.
        puml_type (str): The name of diagram type. Will be used in the result message.
        puml_content_function (callable): The diagram-specific generation function. Must return an array of the diagram file contents by line.

    Returns:
        Result message string
    """
    with validation(parser.parse_file, architecture_file_path) as result:
        file_name, _ = os.path.splitext(os.path.basename(architecture_file_path))
        puml_lines = puml_content_function(result.model)
        puml_output_string = "\n".join(puml_lines)

        if output_directory:
            output_file_path = os.path.join(output_directory, f"{file_name}{PLANT_UML_FILE_EXTENSION}")

            with open(output_file_path, "w") as out_file:
                out_file.write(puml_output_string)

            return f"Wrote PUML {puml_type} diagram to {output_file_path}."

        else:
            return f"File: {architecture_file_path}\n{puml_output_string}\n"


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
