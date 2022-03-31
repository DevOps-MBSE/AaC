"""This module contains helpers for creating Definitions for use with unit tests."""

import yaml

from aac.lang.definitions.definition import Definition

ACTION_STRING = "action"
ARGUMENTS_STRING = "arguments"
ADD_STRING = "add"
BEHAVIOR_STRING = "behavior"
COMPONENTS_STRING = "components"
DESCRIPTION_STRING = "description"
FIELDS_STRING = "fields"
NAME_STRING = "name"
PARTICIPANTS_STRING = "participants"
REQUIRED_STRING = "required"
SOURCE_STRING = "source"
STATE_STRING = "state"
STEP_STRING = "step"
STEPS_STRING = "steps"
TARGET_STRING = "target"
TYPE_STRING = "type"
VALIDATION_STRING = "validation"


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


def create_enum_definition(name: str, values: list[str]):
    """Return a simulated enum definition."""

    definition_dict = {NAME_STRING: name, "values": values}

    return _create_parsed_defintion("enum", definition_dict)


def create_data_definition(name: str, fields: list[dict] = [], required: list[str] = [], validation: list[dict] = []):
    """Return a simulated data definition."""
    definition_dict = {
        NAME_STRING: name,
        FIELDS_STRING: fields,
        REQUIRED_STRING: required,
        VALIDATION_STRING: validation,
    }

    return _create_parsed_defintion("data", definition_dict)


def create_usecase_definition(name: str, description: str, participants: list[dict] = [], steps: list[dict] = []):
    """Return a simulated usecase definition."""
    definition_dict = {
        NAME_STRING: name,
        DESCRIPTION_STRING: description,
        PARTICIPANTS_STRING: participants,
        STEPS_STRING: steps,
    }

    return _create_parsed_defintion("usecase", definition_dict)


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

    return _create_parsed_defintion("model", definition_dict)


def create_data_ext_definition(name: str, type: str, fields: list[dict] = [], required: list[dict] = []):
    """Return a simulated data extension definition."""
    definition_dict = {
        NAME_STRING: name,
        TYPE_STRING: type,
        "dataExt": {
            ADD_STRING: fields,
            REQUIRED_STRING: required,
        },
    }

    return _create_parsed_defintion("ext", definition_dict)


def create_enum_ext_definition(name: str, type: str, values: list[str] = []):
    """Return a simulated data extension definition."""
    definition_dict = {
        NAME_STRING: name,
        TYPE_STRING: type,
        "enumExt": {
            ADD_STRING: values,
        },
    }
    return _create_parsed_defintion("ext", definition_dict)


def _create_parsed_defintion(root_key: str, definition_structure: dict):
    """The base Parsed Definition creation function."""
    name = (NAME_STRING in definition_structure and definition_structure[NAME_STRING]) or "undefined_name"
    definition_dict = {root_key: definition_structure}

    return Definition(
        name=name, content=yaml.dump(definition_dict, sort_keys=False), lexemes=[], structure=definition_dict
    )
