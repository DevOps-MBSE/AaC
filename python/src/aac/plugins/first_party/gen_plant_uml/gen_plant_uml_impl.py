"""AaC Plugin implementation module for the Generate PlantUML Diagrams plugin."""

import os

from typing import Callable, Optional

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.search import search_definition
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.templates.engine import generate_templates, load_templates, write_generated_templates_to_file
from aac.validate import validated_source

plugin_name = "Generate PlantUML Diagrams"
PLANT_UML_FILE_EXTENSION = ".puml"
COMPONENT_STRING = "component"
OBJECT_STRING = "object"
SEQUENCE_STRING = "sequence"
REQUIREMENTS_STRING = "requirements"
FILE_NAME_CHARACTERS_TO_REPLACE = ".!@#$%^&*();,\\/?[]{}`~|'"


def puml_requirements(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Generate a requirements diagram from the requirements of a system modeled with AaC.

    Args:
        architecture_file (str): Path to an AaC file containing modeled requirements from which to generate a requirements diagram.
        output_directory (str): Output directory for the PlantUML (.puml) diagram file.
    """
    architecture_file_path = os.path.abspath(architecture_file)

    def get_requirement_type(attributes: list[dict]) -> str:
        if not attributes:
            attributes = [{"name": "type", "value": None}]

        requirement_types = [attr.get("value") for attr in attributes if attr.get("name") == "type"]
        return f"{requirement_types[0]}Requirement" if requirement_types else "requirement"

    def get_all_requirements(specification: Definition) -> list[dict]:
        requirements = [req for req in specification.get_top_level_fields().get("requirements", [])]
        for section in specification.get_top_level_fields().get("sections", []):
            requirements.extend(section.get("requirements", []))

        return requirements

    def get_requirement_ancestry(requirement_id: str, other_requirement: dict, direction: str, other_direction: str) -> Optional[dict]:
        if requirement_id in other_requirement.get(direction, {}).get("ids", []):
            other_requirement_id = other_requirement.get("id", "")
            return {
                direction: f"req{requirement_id.translate(requirement_id_translator)}",
                other_direction: f"req{other_requirement_id.translate(requirement_id_translator)}",
                # TODO: Handle different types of arrows
                "arrow": "<..",
                # TODO: Handle different types of labels
                "label": "refine",
            }

    def get_child_requirements(requirement_id: str, other_requirement: dict) -> Optional[dict]:
        return get_requirement_ancestry(requirement_id, other_requirement, "child", "parent")

    def get_parent_requirements(requirement_id: str, other_requirement: dict) -> Optional[dict]:
        return get_requirement_ancestry(requirement_id, other_requirement, "parent", "child")

    def get_connected_requirements(requirement: dict, requirement_structures: list[dict], connected_requirements: list[dict]):
        if not requirement_structures:
            return connected_requirements

        first, *rest = requirement_structures
        if requirement != first:
            requirement_id = requirement.get("id", "")

            child = get_child_requirements(requirement_id, first)
            if child:
                connected_requirements.append(child)

            parent = get_parent_requirements(requirement_id, first)
            if parent:
                connected_requirements.append(parent)

        return get_connected_requirements(requirement, rest, connected_requirements)

    def generate_requirements_diagram(definitions: list[Definition]):
        spec_definitions = get_definitions_by_root_key("spec", definitions)
        requirement_structures = [req for spec in spec_definitions for req in get_all_requirements(spec)]

        requirements = []
        for structure in requirement_structures:
            requirement_id = structure.get("id", "")
            attributes = structure.get("attributes", [])
            requirements.append({
                "type": get_requirement_type(attributes),
                # TODO: Handle titles for requirements
                "title": structure.get("name"),
                "name": f"req{requirement_id.translate(requirement_id_translator)}",
                "id": requirement_id,
                "shall": structure.get("shall"),
                "attributes": attributes,
                "connected": get_connected_requirements(structure, requirement_structures, []),
            })

        aac_file_name = _extract_aac_file_name(architecture_file)
        generated_file_name = _get_generated_file_name(aac_file_name, REQUIREMENTS_STRING, "", output_directory)

        return [{"title": "", "filename": generated_file_name, "requirements": requirements}]

    requirement_id_translator = str.maketrans({".": "_", "-": "_"})
    with plugin_result(
        plugin_name,
        _generate_diagram_to_file,
        architecture_file_path,
        output_directory,
        REQUIREMENTS_STRING,
        generate_requirements_diagram,
    ) as result:
        return result


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
            generated_file_name = _get_generated_file_name(aac_file_name, SEQUENCE_STRING, use_case_title, output_directory)
            properties.append(
                {
                    "filename": generated_file_name,
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
        generated_filename = _get_generated_file_name(aac_file_name, OBJECT_STRING, model_name, output_directory)
        return [
            {
                "filename": generated_filename,
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
