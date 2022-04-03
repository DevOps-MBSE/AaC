"""Module for AaC Language functions related to definition references."""

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.definition import Definition


def get_definition_references_from_context(source_definition: Definition) -> list[Definition]:
    """
    Return a list of Definitions from the current active language context that reference the source_definition.

    Args:
        source_definition (Definition): The definition that is being referenced

    Return:
        A list of Definitions that reference the source_definition_name
    """
    active_context = get_active_context()
    return get_definition_references_from_list(source_definition, active_context.definitions)


def get_definition_references_from_list(source_definition: Definition, definitions_to_search: list[Definition]) -> list[Definition]:
    """
    Return a subset of Definitions that reference the source_definition.

    Args:
        source_definition (Definition): The definition that is being referenced
        definitions_to_search (list[Definition]): The definitions to search through for references

    Return:
        A list of Definitions that reference the source_definition_name
    """
    def _filter_definitions_by_reference(definition_to_filter: Definition) -> bool:
        return f"type: {source_definition.name}" in definition_to_filter.to_yaml()

    return list(filter(_filter_definitions_by_reference, definitions_to_search))
