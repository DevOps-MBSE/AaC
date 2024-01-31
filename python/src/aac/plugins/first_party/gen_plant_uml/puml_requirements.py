"""A module used to generate a requirements diagram."""

from typing import Optional

from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.definition import Definition
from aac.plugins.first_party.gen_plant_uml.puml_helpers import extract_aac_file_name, get_generated_file_name

REQUIREMENTS_STRING = "requirements"
requirement_id_translator = str.maketrans({".": "_", "-": "_"})


def generate_requirements_diagram(architecture_file: str, output_directory: str, definitions: list[Definition]):
    """
    Generate a requirements diagram using the PlantUML framework.

    Args:
        architecture_file (str): The file from which to get the AaC definitions.
        output_directory (str): The directory in which to place generated diagram output.
        definitions (list[Definition]): A list of AaC definitions from which to pull the requirements.
    """
    spec_definitions = get_definitions_by_root_key("spec", definitions)
    requirement_structures = [req for spec in spec_definitions for req in _get_all_requirements(spec)]

    requirements = []
    for structure in requirement_structures:
        requirement_id = structure.get("id", "")
        attributes = structure.get("attributes", [])
        requirements.append(
            {
                "type": _get_requirement_type(attributes),
                "title": None,
                "name": f"req{requirement_id.translate(requirement_id_translator)}",
                "id": requirement_id,
                "shall": structure.get("shall", "").replace("\n", " "),
                "attributes": attributes,
                "connected": _get_connected_requirements(structure, requirement_structures, []),
            }
        )

    spec_definition = spec_definitions[0]
    aac_file_name = extract_aac_file_name(architecture_file)
    generated_file_name = get_generated_file_name(aac_file_name, REQUIREMENTS_STRING, spec_definition.name, output_directory)
    return [
        {
            "title": spec_definition.name,
            "subtitle": spec_definition.get_description(),
            "package": "Default",
            "filename": generated_file_name,
            "requirements": requirements,
        }
    ]


def _get_requirement_type(attributes: list[dict]) -> str:
    if not attributes:
        attributes = [{}]

    requirement_types = [attr.get("value") for attr in attributes if attr.get("name") == "type"]
    return f"{requirement_types[0]}Requirement" if requirement_types else "requirement"


def _get_all_requirements(specification: Definition) -> list[dict]:
    requirements = [req for req in specification.get_top_level_fields().get("requirements", [])]
    for section in specification.get_top_level_fields().get("sections", []):
        requirements.extend(section.get("requirements", []))

    return requirements


def _get_requirement_ancestry(
    requirement_id: str, other_requirement: dict, direction: str, other_direction: str
) -> Optional[dict]:
    if requirement_id in other_requirement.get(direction, {}).get("ids", []):
        other_requirement_id = other_requirement.get("id", "")
        return {
            direction: f"req{requirement_id.translate(requirement_id_translator)}",
            other_direction: f"req{other_requirement_id.translate(requirement_id_translator)}",
            "arrow": "+--",
            "relationship": "",
        }


def _get_child_requirements(requirement_id: str, other_requirement: dict) -> Optional[dict]:
    return _get_requirement_ancestry(requirement_id, other_requirement, "child", "parent")


def _get_parent_requirements(requirement_id: str, other_requirement: dict) -> Optional[dict]:
    return _get_requirement_ancestry(requirement_id, other_requirement, "parent", "child")


def _get_connected_requirements(requirement: dict, requirement_structures: list[dict], connected_requirements: list[dict]):
    if not requirement_structures:
        return connected_requirements

    first, *rest = requirement_structures
    if requirement != first:
        requirement_id = requirement.get("id", "")

        child = _get_child_requirements(requirement_id, first)
        if child:
            connected_requirements.append(child)

        parent = _get_parent_requirements(requirement_id, first)
        if parent:
            connected_requirements.append(parent)

    return _get_connected_requirements(requirement, rest, connected_requirements)
