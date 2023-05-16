"""This module provides functions to collate and build a meta structure for an AaC definition."""

from copy import deepcopy
from typing import Any, Optional

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.lexeme import Lexeme
from aac.lang.definitions.schema import get_root_schema_definitions, get_schema_for_field
from aac.lang.definitions.structural_node import NodeType, StructuralNode
from aac.lang.language_context import LanguageContext


def compute_metadata_structure(definition: Definition, language_context: LanguageContext) -> None:
    """
    Builds the metadata structure for the definition and attaches it to the passed-in definition's `meta_structure` attribute.

    Args:
        definition (Definition): The definition for which to compute a meta-structure.
        language_context (LanguageContext): The language context used to provide the metadata.
    """
    token_traversal_list = definition.lexemes.copy()  # Create a copy to avoid altering the referenced list
    yaml_traversal_structure = deepcopy(definition.structure)  # Create a copy to avoid altering the referenced yaml structure

    root_token = token_traversal_list.pop(0)
    root_definition = get_root_schema_definitions(language_context).get(root_token.value)

    root_node = StructuralNode(NodeType.ROOT_KEY, root_definition, root_token, None, [])
    root_yaml_structure = yaml_traversal_structure.get(root_token.value, {})
    _recursive_meta_structure_build(
        definition, token_traversal_list, root_yaml_structure, root_node, [root_token.value], language_context
    )

    definition.meta_structure = root_node


def _recursive_meta_structure_build(
    definition: Definition,
    tokens: list[Lexeme],
    yaml_structure: dict[str, Any],
    parent_node: StructuralNode,
    traversed_keys: list[str],
    language_context: LanguageContext,
) -> None:
    """Recursively builds the meta-structure nodes and attaches them to the parent node."""

    child_nodes = []

    def _create_node(
        node_type: NodeType, node_token: Optional[Lexeme] = None, defining_definition: Optional[Definition] = None
    ) -> StructuralNode:
        new_node = StructuralNode(node_type, defining_definition, node_token, parent_node, [])
        child_nodes.append(new_node)
        return new_node

    def _get_node_token_keys_and_definition() -> tuple[Lexeme, list[str], Optional[Definition]]:
        node_token = tokens.pop(0)
        node_value = node_token.value
        node_traversal_keys = [*traversed_keys, node_value]
        node_definition = get_schema_for_field(definition, node_traversal_keys, language_context)
        return node_token, node_traversal_keys, node_definition

    if isinstance(yaml_structure, list):
        for child_structure in yaml_structure:
            list_entry_node = _create_node(NodeType.LIST_ENTRY)
            _recursive_meta_structure_build(
                definition, tokens, child_structure, list_entry_node, traversed_keys, language_context
            )

    elif isinstance(yaml_structure, dict):
        for child_value in yaml_structure.values():
            node_token, traversal_keys, node_definition = _get_node_token_keys_and_definition()
            new_node = _create_node(NodeType.SCHEMA_STRUCTURE, node_token, node_definition)
            _recursive_meta_structure_build(definition, tokens, child_value, new_node, traversal_keys, language_context)

    else:
        node_token, traversal_keys, node_definition = _get_node_token_keys_and_definition()
        node_definition = get_schema_for_field(definition, traversal_keys, language_context)

        node_type = NodeType.ENUM_VALUE
        if node_definition == language_context.get_primitives_definition():
            node_type = NodeType.PRIMITIVE_VALUE

        new_node = _create_node(node_type, node_token, node_definition)

    parent_node.children.extend(child_nodes)
