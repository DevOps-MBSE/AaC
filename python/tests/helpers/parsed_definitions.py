"""This module contains helpers for creating Definitions for use with unit tests."""

import yaml

from aac.io.files.aac_file import AaCFile
from aac.lang.definitions.definition import Definition

ACCEPTANCE_STRING = "acceptance"
ACTION_STRING = "action"
ADD_STRING = "add"
ARGUMENTS_STRING = "arguments"
BEHAVIOR_CAPITALIZED_STRING = "Behavior"
BEHAVIOR_STRING = "behavior"
COMPONENTS_STRING = "components"
INHERITS_STRING = "inherits"
DESCRIPTION_STRING = "description"
FIELDS_STRING = "fields"
GIVEN_STRING = "given"
INPUT_STRING = "input"
NAME_STRING = "name"
OUTPUT_STRING = "output"
PARTICIPANTS_STRING = "participants"
REQUIRED_STRING = "required"
SCENARIO_STRING = "scenario"
SOURCE_STRING = "source"
STATE_STRING = "state"
STEP_STRING = "step"
STEPS_STRING = "steps"
TAGS_STRING = "tags"
TARGET_STRING = "target"
THEN_STRING = "then"
TYPE_STRING = "type"
VALIDATION_STRING = "validation"
WHEN_STRING = "when"


def create_field_entry(name: str, type: str = "", description: str = "") -> dict:
    """
    Creates a single field entry for definitions.

    Use this function to create a field entries for the "fields" section of larger definitions.

    Returns:
        A dictionary representing an AaC Field definition.
    """
    return {
        NAME_STRING: name,
        TYPE_STRING: type,
        DESCRIPTION_STRING: description,
    }


def create_step_entry(title: str, source: str, target: str, action: str) -> dict:
    """
    Creates a single step entry for definitions.

    Use this function to create a step entry for the "steps" section of larger definitions.

    Returns:
        A dictionary representing an AaC Step definition.
    """
    return {
        STEP_STRING: title,
        SOURCE_STRING: source,
        TARGET_STRING: target,
        ACTION_STRING: action,
    }


def create_validation_entry(name: str, arguments: list[str] = []) -> dict:
    """
    Creates a single validation entry for definitions.

    Use this function to create a field entries for the "validation" section of larger definitions.

    Returns:
        A dictionary representing an AaC validation definition.
    """
    return {
        NAME_STRING: name,
        ARGUMENTS_STRING: arguments,
    }


def create_behavior_entry(name: str, behavior_type: str = "pub-sub", description: str = "", tags: list[str] = [], input: list[dict] = [], output: list[dict] = [], acceptance: list[dict] = []) -> dict:
    """
    Creates a single behavior entry for definitions.

    Use this function to create a field entries for the "behavior" section of larger definitions.

    Returns:
        A dictionary representing an AaC behavior definition.
    """
    return {
        NAME_STRING: name,
        TYPE_STRING: behavior_type,
        DESCRIPTION_STRING: description,
        TAGS_STRING: tags,
        INPUT_STRING: input,
        OUTPUT_STRING: output,
        ACCEPTANCE_STRING: acceptance,
    }


def create_scenario_entry(name: str, tags: list[str] = [], given: list[str] = [], when: list[str] = [], then: list[str] = []) -> dict:
    """
    Creates a single scenario entry for definitions.

    Use this function to create a field entries for the "scenario" section of larger definitions.

    Returns:
        A dictionary representing an AaC scenario definition.
    """
    return {
        NAME_STRING: name,
        TAGS_STRING: tags,
        GIVEN_STRING: given,
        WHEN_STRING: when,
        THEN_STRING: then
    }


def create_enum_definition(name: str, values: list[str]):
    """Return a simulated enum definition."""

    definition_dict = {NAME_STRING: name, "values": values}

    return _create_parsed_definition("enum", definition_dict)


def create_schema_definition(name: str, description: str = "", fields: list[dict] = [], validations: list[dict] = [], inherits: list[str] = []):
    """Return a simulated schema definition."""
    definition_dict = {NAME_STRING: name}

    if inherits:
        definition_dict[INHERITS_STRING] = inherits

    if description:
        definition_dict[DESCRIPTION_STRING] = description

    # Placing this here to preserve an expected order
    definition_dict[FIELDS_STRING] = fields

    if validations:
        definition_dict[VALIDATION_STRING] = validations

    return _create_parsed_definition("schema", definition_dict)


def create_usecase_definition(name: str, description: str, participants: list[dict] = [], steps: list[dict] = []):
    """Return a simulated usecase definition."""
    definition_dict = {
        NAME_STRING: name,
        DESCRIPTION_STRING: description,
        PARTICIPANTS_STRING: participants,
        STEPS_STRING: steps,
    }

    return _create_parsed_definition("usecase", definition_dict)


def create_model_definition(
    name: str, description: str = "", components: list[dict] = [], behavior: list[dict] = [], state: list[str] = []
):
    """Return a simulated model definition."""
    definition_dict = {
        NAME_STRING: name,
        DESCRIPTION_STRING: description,
        COMPONENTS_STRING: components,
        BEHAVIOR_STRING: behavior,
        STATE_STRING: state,
    }

    return _create_parsed_definition("model", definition_dict)


def create_schema_ext_definition(name: str, type: str, description: str = "", fields: list[dict] = [], required: list[str] = []):
    """Return a simulated schema extension definition."""
    definition_dict = {
        NAME_STRING: name,
        TYPE_STRING: type,
        DESCRIPTION_STRING: description,
        "schemaExt": {
            ADD_STRING: fields,
            REQUIRED_STRING: required,
        },
    }

    return _create_parsed_definition("ext", definition_dict)


def create_enum_ext_definition(name: str, type: str, description: str = "", values: list[str] = []):
    """Return a simulated enum extension definition."""
    definition_dict = {
        NAME_STRING: name,
        TYPE_STRING: type,
        DESCRIPTION_STRING: description,
        "enumExt": {
            ADD_STRING: values,
        },
    }
    return _create_parsed_definition("ext", definition_dict)


def create_validation_definition(name: str, description: str = "", behavior: list[dict] = []):
    """Return a simulated validation definition."""
    definition_dict = {
        NAME_STRING: name,
        DESCRIPTION_STRING: description,
        BEHAVIOR_STRING: behavior,
    }

    return _create_parsed_definition("validation", definition_dict)


def _create_parsed_definition(root_key: str, definition_structure: dict) -> Definition:
    """The base Parsed Definition creation function."""
    name = (NAME_STRING in definition_structure and definition_structure[NAME_STRING]) or "undefined_name"
    definition_dict = {root_key: definition_structure}
    definition_source = AaCFile("<test>", False, False)

    return Definition(
        name=name, content=yaml.dump(definition_dict, sort_keys=False), source=definition_source, lexemes=[], structure=definition_dict
    )
