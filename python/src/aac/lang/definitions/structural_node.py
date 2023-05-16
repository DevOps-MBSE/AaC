"""Provides nodes for decomposing the definition's structure, collating metadata, and providing other QOL improvements."""
from __future__ import annotations
from enum import Enum, auto
from typing import Optional
from attr import attrib, attrs, validators

import typing

if typing.TYPE_CHECKING:
    # Have to perform this typing check import to avoid circular dependencies while maintaining type hinting.
    from aac.lang.definitions.definition import Definition

from aac.lang.definitions.lexeme import Lexeme


class NodeType(Enum):
    """Enumeration values to easily distinguish structural node types."""
    SCHEMA_STRUCTURE = auto()
    ENUM_VALUE = auto()
    ROOT_KEY = auto()
    LIST_ENTRY = auto()
    PRIMITIVE_VALUE = auto()


@attrs(hash=False, eq=False)
class StructuralNode:
    """
    An Architecture-as-Code definition structural node.

    These nodes are used to build a traversable tree for the definition's structure as opposed to leveraging the
        unstructured dictionaries, lists, and primitives supplied by just parsing the yaml structure.

    Attributes:
        node_type (NodeType): Enum value used to quickly distinguish between node types.
        defining_definition (Optional[Definition]): The `Definition` that defines the structure or enumeration values for the token.
        token (Optional[Lexeme]): The corresponding token within the definition's yaml structure. Optional as nodes representing entries in a list will not have tokens.
        parent (Optional[StructuralNode]): Reference to the node's parent; None if the node is the root node.
        children (List[StructuralNode]): Reference the the node's children; empty if there are no children.
    """
    node_type: NodeType = attrib(validator=validators.instance_of(NodeType))
    defining_definition: Optional['Definition'] = attrib()  # Can't reference Definition here for validation without creating a circular dependency.
    token: Optional[Lexeme] = attrib(validator=validators.optional(validators.instance_of(Lexeme)))
    parent: Optional[StructuralNode] = attrib()  # Python/Attrs isn't capable of supporting self-referencing types for self-referential type validator
    children: list[StructuralNode] = attrib(validator=validators.instance_of(list))

    def __init__(self, node_type: NodeType, defining_definition: Optional['Definition'] = None, token: Optional[Lexeme] = None, parent: Optional[StructuralNode] = None, children: list[StructuralNode] = []):
        """
        Initialize a Structural Node object.

        Args:
            node_type (NodeType): Enum value used to quickly distinguish between node types
            defining_definition (Optional[Definition]): The definition that defines the structure or enumeration values for the token.
            token (Optional[Lexeme]): The corresponding token within the definition's yaml structure. Optional as nodes representing entries in a list will not have tokens.
            parent (Optional[StructuralNode]): Reference to the node's parent; null if the node is the root node.
            children (List[StructuralNode]): Reference the the node's children; empty if there are no children.
        """
        self.node_type = node_type
        self.defining_definition = defining_definition
        self.token = token
        self.parent = parent
        self.children = children
