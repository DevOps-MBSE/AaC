"""Provides a number of helper functions to programmatically build the various SysML definitions."""

from aac.io.parser import parse
from aac.lang.constants import (
    DEFINITION_FIELD_BEHAVIOR,
    DEFINITION_FIELD_COMPONENTS,
    DEFINITION_FIELD_DESCRIPTION,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_STATE,
    DEFINITION_FIELD_TYPE,
    ROOT_KEY_MODEL,
)
from aac.lang.definitions.definition import Definition
from aac.plugins.first_party.sysml.constants import (
    SYSML_DEFINITION_FIELD_BLOCKS,
    SYSML_DEFINITION_FIELD_DEFAULT_NAMESPACE,
    SYSML_DEFINITION_FIELD_VALUES,
    SYSML_ROOT_KEY_BDD,
    SYSML_ROOT_KEY_BLOCK,
)
import yaml


def create_block_definition_diagram(name: str, default_namespace: str, blocks: list = []) -> Definition:
    """Creates a block definition diagram definition."""
    fields = {
        SYSML_DEFINITION_FIELD_DEFAULT_NAMESPACE: default_namespace,
        SYSML_DEFINITION_FIELD_BLOCKS: blocks,
    }

    return _create_definition(SYSML_ROOT_KEY_BDD, name, fields)


def create_block(name: str, values: dict = {}) -> Definition:
    """Creates a block definition."""
    fields = {
        SYSML_DEFINITION_FIELD_VALUES: values,
    }

    return _create_definition(SYSML_ROOT_KEY_BLOCK, name, fields)


def create_model(
    name: str,
    description: str = "",
    components: list[dict] = [],
    behavior: list[dict] = [],
    state: list[str] = [],
) -> Definition:
    """Creates a model definition."""
    fields = {
        DEFINITION_FIELD_NAME: name,
        DEFINITION_FIELD_DESCRIPTION: description,
        DEFINITION_FIELD_COMPONENTS: components,
        DEFINITION_FIELD_BEHAVIOR: behavior,
        DEFINITION_FIELD_STATE: state,
    }

    return _create_definition(ROOT_KEY_MODEL, name, fields)


def create_field_entry(name: str, type: str, description: str) -> dict:
    """Used to create a field entry for definitions."""
    return {DEFINITION_FIELD_NAME: name, DEFINITION_FIELD_TYPE: type, DEFINITION_FIELD_DESCRIPTION: description}


def _create_definition(root_key: str, name: str, fields: dict = {}) -> Definition:
    """Create a definition given the root key, name, and fields."""
    name_field = {DEFINITION_FIELD_NAME: name}
    definition_dict = {root_key: name_field | fields}
    return parse(yaml.dump(definition_dict, sort_keys=False), "<builder>")[0]
