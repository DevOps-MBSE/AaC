"""Module for AaC Language functions related to definition references."""

from aac.parser import ParsedDefinition
from aac.lang.context_manager import get_active_context


def get_definition_references_from_context(source_definition: ParsedDefinition) -> list[ParsedDefinition]:
    """
    Return a list of ParsedDefinitions from the current ActiveContext that reference the source_definition.

    Args:
        source_definition: The definition that is being referenced

    Return:
        A list of ParsedDefinitions that reference the source_definition_name
    """
    active_context = get_active_context()
    return get_definition_references_from_list(source_definition, active_context.definitions)


def get_definition_references_from_list(source_definition: ParsedDefinition, definitions_to_search: list[ParsedDefinition]) -> list[ParsedDefinition]:
    """
    Return a subset of ParsedDefinitions that reference the source_definition.

    Args:
        source_definition: The definition that is being referenced
        definitions_to_search: The definitions to search through for references

    Return:
        A list of ParsedDefinitions that reference the source_definition_name
    """
    def _filter_definitions_by_reference(definition_to_filter: ParsedDefinition) -> bool:
        return f"type: {source_definition.name}" in definition_to_filter.to_yaml()

    return list(filter(_filter_definitions_by_reference, definitions_to_search))
