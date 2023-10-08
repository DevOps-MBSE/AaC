"""This module contains helpers for creating Definitions for use with unit tests."""
import yaml

from aac.io.parser import parse, ParserError
from aac.lang.constants import (
    BEHAVIOR_TYPE_PUBLISH_SUBSCRIBE,
    DEFINITION_FIELD_ACCEPTANCE,
    DEFINITION_FIELD_ACTION,
    DEFINITION_FIELD_ADD,
    DEFINITION_FIELD_ARGUMENTS,
    DEFINITION_FIELD_ATTRIBUTES,
    DEFINITION_FIELD_BEHAVIOR,
    DEFINITION_FIELD_CHILD,
    DEFINITION_FIELD_COMMANDS,
    DEFINITION_FIELD_COMPONENTS,
    DEFINITION_FIELD_DEFINITION_SOURCES,
    DEFINITION_FIELD_DEFINITION_VALIDATIONS,
    DEFINITION_FIELD_DESCRIPTION,
    DEFINITION_FIELD_EXTENSION_ENUM,
    DEFINITION_FIELD_EXTENSION_SCHEMA,
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_FILES,
    DEFINITION_FIELD_GIVEN,
    DEFINITION_FIELD_ID,
    DEFINITION_FIELD_IDS,
    DEFINITION_FIELD_INHERITS,
    DEFINITION_FIELD_INPUT,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_OUTPUT,
    DEFINITION_FIELD_PARENT,
    DEFINITION_FIELD_PARTICIPANTS,
    DEFINITION_FIELD_PRIMITIVE_VALIDATIONS,
    DEFINITION_FIELD_REQUIRED,
    DEFINITION_FIELD_REQUIREMENTS,
    DEFINITION_FIELD_ROOT,
    DEFINITION_FIELD_SCENARIO,
    DEFINITION_FIELD_SECTIONS,
    DEFINITION_FIELD_SHALL,
    DEFINITION_FIELD_SOURCE,
    DEFINITION_FIELD_STATE,
    DEFINITION_FIELD_STEP,
    DEFINITION_FIELD_STEPS,
    DEFINITION_FIELD_TAGS,
    DEFINITION_FIELD_TARGET,
    DEFINITION_FIELD_THEN,
    DEFINITION_FIELD_TYPE,
    DEFINITION_FIELD_VALIDATION,
    DEFINITION_FIELD_VALUE,
    DEFINITION_FIELD_VALUES,
    DEFINITION_FIELD_WHEN,
    ROOT_KEY_IMPORT,
    ROOT_KEY_ENUM,
    ROOT_KEY_EXTENSION,
    ROOT_KEY_MODEL,
    ROOT_KEY_PLUGIN,
    ROOT_KEY_SCHEMA,
    ROOT_KEY_SPECIFICATION,
    ROOT_KEY_USECASE,
    ROOT_KEY_VALIDATION,
)
from aac.lang.definitions.definition import Definition


def create_field_entry(name: str, type: str = "", description: str = "") -> dict:
    """
    Creates a single field entry for definitions.

    Use this function to create a field entries for the "fields" section of larger definitions.

    Returns:
        A dictionary representing an AaC Field definition.
    """
    return {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_TYPE: type,
        DEFINITION_FIELD_DESCRIPTION: description,
    }


def create_step_entry(title: str, source: str, target: str, action: str) -> dict:
    """
    Creates a single step entry for definitions.

    Use this function to create a step entry for the "steps" section of larger definitions.

    Returns:
        A dictionary representing an AaC Step definition.
    """
    return {
        DEFINITION_FIELD_STEP: title,
        DEFINITION_FIELD_SOURCE: source,
        DEFINITION_FIELD_TARGET: target,
        DEFINITION_FIELD_ACTION: action,
    }


def create_validation_entry(name: str, arguments: list[str] = []) -> dict:
    """
    Creates a single validation entry for definitions.

    Use this function to create a field entries for the "validation" section of larger definitions.

    Returns:
        A dictionary representing an AaC validation definition.
    """
    return {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_ARGUMENTS: arguments,
    }


def create_behavior_entry(
    name: str,
    behavior_type: str = BEHAVIOR_TYPE_PUBLISH_SUBSCRIBE,
    description: str = "",
    tags: list[str] = [],
    input: list[dict] = [],
    output: list[dict] = [],
    acceptance: list[dict] = [],
    requirements: list[str] = [],
) -> dict:
    """
    Creates a single behavior entry for definitions.

    Use this function to create a field entries for the "behavior" section of larger definitions.

    Returns:
        A dictionary representing an AaC behavior definition.
    """
    return {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_TYPE: behavior_type,
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_TAGS: tags,
        DEFINITION_FIELD_INPUT: input,
        DEFINITION_FIELD_OUTPUT: output,
        DEFINITION_FIELD_ACCEPTANCE: acceptance,
        DEFINITION_FIELD_REQUIREMENTS: {DEFINITION_FIELD_IDS: requirements},
    }


def create_scenario_entry(
    name: str, tags: list[str] = [], given: list[str] = [], when: list[str] = [], then: list[str] = []
) -> dict:
    """
    Creates a single scenario entry for definitions.

    Use this function to create a field entries for the "scenario" section of larger definitions.

    Returns:
        A dictionary representing an AaC scenario definition.
    """
    return {
        DEFINITION_FIELD_SCENARIO: name,
        DEFINITION_FIELD_TAGS: tags,
        DEFINITION_FIELD_GIVEN: given,
        DEFINITION_FIELD_WHEN: when,
        DEFINITION_FIELD_THEN: then,
    }


def create_enum_definition(name: str, values: list[str]):
    """Return a simulated enum definition."""

    definition_dict = {DEFINITION_FIELD_NAME: name, DEFINITION_FIELD_VALUES: values}

    return create_definition(ROOT_KEY_ENUM, name, definition_dict)


def create_schema_definition(
    name: str,
    root: str = "",
    description: str = "",
    fields: list[dict] = [],
    validations: list[dict] = [],
    inherits: list[str] = [],
):
    """Return a simulated schema definition."""
    definition_dict = {DEFINITION_FIELD_NAME: name}

    if inherits:
        definition_dict[DEFINITION_FIELD_INHERITS] = inherits

    if description:
        definition_dict[DEFINITION_FIELD_DESCRIPTION] = description

    if root:
        definition_dict[DEFINITION_FIELD_ROOT] = root

    # Placing this here to preserve an expected order
    definition_dict[DEFINITION_FIELD_FIELDS] = fields

    if validations:
        definition_dict[DEFINITION_FIELD_VALIDATION] = validations

    return create_definition(ROOT_KEY_SCHEMA, name, definition_dict)


def create_usecase_definition(name: str, description: str = "", participants: list[dict] = [], steps: list[dict] = []):
    """Return a simulated usecase definition."""
    definition_dict = {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_PARTICIPANTS: participants,
        DEFINITION_FIELD_STEPS: steps,
    }

    return create_definition(ROOT_KEY_USECASE, name, definition_dict)


def create_model_definition(
    name: str,
    description: str = "",
    components: list[dict] = [],
    behavior: list[dict] = [],
    state: list[str] = [],
    requirements: list[str] = [],
):
    """Return a simulated model definition."""
    definition_dict = {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_COMPONENTS: components,
        DEFINITION_FIELD_BEHAVIOR: behavior,
        DEFINITION_FIELD_STATE: state,
    }

    if requirements:
        definition_dict = definition_dict | {DEFINITION_FIELD_REQUIREMENTS: {DEFINITION_FIELD_IDS: requirements}}

    return create_definition(ROOT_KEY_MODEL, name, definition_dict)


def create_schema_ext_definition(
    name: str, type: str, description: str = "", fields: list[dict] = [], required: list[str] = []
):
    """Return a simulated schema extension definition."""
    definition_dict = {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_TYPE: type,
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_EXTENSION_SCHEMA: {
            DEFINITION_FIELD_ADD: fields,
            DEFINITION_FIELD_REQUIRED: required,
        },
    }

    return create_definition(ROOT_KEY_EXTENSION, name, definition_dict)


def create_enum_ext_definition(name: str, type: str, description: str = "", values: list[str] = []):
    """Return a simulated enum extension definition."""
    definition_dict = {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_TYPE: type,
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_EXTENSION_ENUM: {
            DEFINITION_FIELD_ADD: values,
        },
    }
    return create_definition(ROOT_KEY_EXTENSION, name, definition_dict)


def create_validation_definition(name: str, description: str = "", behavior: list[dict] = []):
    """Return a simulated validation definition."""
    definition_dict = {
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_BEHAVIOR: behavior,
    }

    return create_definition(ROOT_KEY_VALIDATION, name, definition_dict)


def create_plugin_definition(
    name: str,
    description: str = "",
    definition_sources: list[str] = [],
    commands: list[dict] = [],
    definition_validations: list[dict] = [],
    primitive_validations: list[dict] = [],
) -> Definition:
    definition_dict = {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_DEFINITION_SOURCES: definition_sources,
        DEFINITION_FIELD_COMMANDS: commands,
        DEFINITION_FIELD_DEFINITION_VALIDATIONS: definition_validations,
        DEFINITION_FIELD_PRIMITIVE_VALIDATIONS: primitive_validations,
    }
    return create_definition(ROOT_KEY_PLUGIN, name, definition_dict)


def create_import_definition(imports: list[str]) -> Definition:
    definition_dict = {DEFINITION_FIELD_FILES: imports}
    return create_definition(ROOT_KEY_IMPORT, "", definition_dict)


def create_spec_definition(
    name: str, description: str = "", requirements: list[dict] = [], sections: list[dict] = []
) -> Definition:
    definition_dict = {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_REQUIREMENTS: requirements,
        DEFINITION_FIELD_SECTIONS: sections,
    }
    return create_definition(ROOT_KEY_SPECIFICATION, name, definition_dict)


def create_spec_section_entry(name: str, description: str = "", requirements: list[dict] = []) -> dict:
    return {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_REQUIREMENTS: requirements,
    }


def create_requirement_entry(
    id: str, shall: str, parent: list[str] = [], child: list[str] = [], attributes: list[dict] = []
) -> dict:
    return {
        DEFINITION_FIELD_ID: id,
        DEFINITION_FIELD_SHALL: shall,
        DEFINITION_FIELD_PARENT: parent,
        DEFINITION_FIELD_CHILD: child,
        DEFINITION_FIELD_ATTRIBUTES: attributes,
    }


def create_requirement_attribute_entry(name: str, value: str) -> dict:
    return {DEFINITION_FIELD_NAME: name, DEFINITION_FIELD_VALUE: value}


def create_definition(root_key: str, name: str, other_fields: dict = {}) -> Definition:
    """The base Parsed Definition creation function."""
    name_field = {DEFINITION_FIELD_NAME: name}
    definition_dict = {root_key: name_field | other_fields}
    try:
        parsed_definitions = parse(yaml.dump(definition_dict, sort_keys=False), "<test>")[0]
    except ParserError as error:
        raise ParserError(error.source, error.errors) from None
    else:
        return parsed_definitions
