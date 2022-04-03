"""Module for AaC Language functions related to definition references."""

from aac.lang.definitions.definition import Definition


def get_definition_references_from_list(
    source_definition: Definition, definitions_to_search: list[Definition]
) -> list[Definition]:
    """
    Return a subset of Definitions that reference the source_definition.

    Args:
        source_definition (Definition): The definition that is being referenced
        definitions_to_search (list[Definition]): The definitions to search through for references

    Return:
        A list of Definitions that reference the source_definition
    """

    def _filter_definitions_by_reference(definition_to_filter: Definition) -> bool:
        return f"type: {source_definition.name}" in definition_to_filter.to_yaml()

    return list(filter(_filter_definitions_by_reference, definitions_to_search))
