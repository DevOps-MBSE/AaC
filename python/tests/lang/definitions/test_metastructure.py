from unittest import TestCase
from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.constants import DEFINITION_NAME_BEHAVIOR, DEFINITION_NAME_BEHAVIOR_TYPE, DEFINITION_NAME_FIELD, DEFINITION_NAME_MODEL, DEFINITION_NAME_PRIMITIVES, DEFINITION_NAME_SCENARIO, DEFINITION_NAME_SCHEMA
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.metadata_structure import compute_metadata_structure
from aac.lang.definitions.structural_node import NodeType, StructuralNode

from tests.helpers.prebuilt_definition_constants import (
    TEST_SCHEMA_A,
    TEST_SERVICE_ONE,
)


class TestDefinitionNodeStructure(TestCase):
    """Exercises' the parser's behavior when building the internal node structure."""

    def test_parser_builds_node_structure_schema(self):

        test_context = get_initialized_language_context()
        test_definition = TEST_SCHEMA_A.copy()

        compute_metadata_structure(test_definition, test_context)

        # Expected defining definition
        schema_definition = test_context.get_definition_by_name(DEFINITION_NAME_SCHEMA)
        primitives_definition = test_context.get_definition_by_name(DEFINITION_NAME_PRIMITIVES)
        field_definition = test_context.get_definition_by_name(DEFINITION_NAME_FIELD)

        # Test that the top node is typed as the root
        definition_structure_root_node = test_definition.meta_structure
        _assert_structural_node(self, definition_structure_root_node, NodeType.ROOT_KEY, schema_definition, 2)

        # Test the top-level field 'name'
        name_node = definition_structure_root_node.children[0]
        _assert_structural_node(self, name_node, NodeType.SCHEMA_STRUCTURE, primitives_definition, 1)

        # Test the value of the top-level field 'name'
        name_value_node = name_node.children[0]
        _assert_structural_node(self, name_value_node, NodeType.PRIMITIVE_VALUE, primitives_definition, 0)

        # Test the top-level field 'fields'
        fields_node = definition_structure_root_node.children[1]
        _assert_structural_node(self, fields_node, NodeType.SCHEMA_STRUCTURE, field_definition, 1)

        # Test the first field entry
        fields_entry1 = fields_node.children[0]
        _assert_structural_node(self, fields_entry1, NodeType.LIST_ENTRY, None, 3)

        # Test the field named 'msg'
        fields_entry1_msg = fields_entry1.children[0]
        _assert_structural_node(self, fields_entry1_msg, NodeType.SCHEMA_STRUCTURE, primitives_definition, 1)

        # Test the msg field's value
        fields_entry1_msg_value = fields_entry1_msg.children[0]
        _assert_structural_node(self, fields_entry1_msg_value, NodeType.PRIMITIVE_VALUE, primitives_definition, 0)

    def test_parser_builds_node_structure_model(self):

        test_context = get_initialized_language_context()
        test_definition = TEST_SERVICE_ONE.copy()

        compute_metadata_structure(test_definition, test_context)

        # Expected defining definition
        model_definition = test_context.get_definition_by_name(DEFINITION_NAME_MODEL)
        primitives_definition = test_context.get_definition_by_name(DEFINITION_NAME_PRIMITIVES)
        field_definition = test_context.get_definition_by_name(DEFINITION_NAME_FIELD)
        behavior_definition = test_context.get_definition_by_name(DEFINITION_NAME_BEHAVIOR)
        behavior_type_definition = test_context.get_definition_by_name(DEFINITION_NAME_BEHAVIOR_TYPE)
        scenario_definition = test_context.get_definition_by_name(DEFINITION_NAME_SCENARIO)

        # Test that the top node is typed as the root
        definition_structure_root_node = test_definition.meta_structure
        _assert_structural_node(self, definition_structure_root_node, NodeType.ROOT_KEY, model_definition, 5)

        # Test the top-level field 'name'
        name_node = definition_structure_root_node.children[0]
        _assert_structural_node(self, name_node, NodeType.SCHEMA_STRUCTURE, primitives_definition, 1)

        # Test the value of the top-level field 'name'
        name_value_node = name_node.children[0]
        _assert_structural_node(self, name_value_node, NodeType.PRIMITIVE_VALUE, primitives_definition, 0)

        # Test the top-level field 'components'
        components_node = definition_structure_root_node.children[2]
        _assert_structural_node(self, components_node, NodeType.SCHEMA_STRUCTURE, field_definition, 0)

        # Test the top-level field 'behavior'
        behaviors_node = definition_structure_root_node.children[3]
        _assert_structural_node(self, behaviors_node, NodeType.SCHEMA_STRUCTURE, behavior_definition, 1)

        # Test the 'behavior' fields entry 1
        behaviors_entry1_node = behaviors_node.children[0]
        _assert_structural_node(self, behaviors_entry1_node, NodeType.LIST_ENTRY, None, 7)

        # Test the 'behavior' fields entry 1 name
        behaviors_entry1_name_node = behaviors_entry1_node.children[0]
        _assert_structural_node(self, behaviors_entry1_name_node, NodeType.SCHEMA_STRUCTURE, primitives_definition, 1)

        # Test the 'behavior' fields entry 1 name value
        behaviors_entry1_name_value_node = behaviors_entry1_name_node.children[0]
        _assert_structural_node(self, behaviors_entry1_name_value_node, NodeType.PRIMITIVE_VALUE, primitives_definition, 0)

        # Test the 'behavior' fields entry 1 type
        behaviors_entry1_type_node = behaviors_entry1_node.children[1]
        _assert_structural_node(self, behaviors_entry1_type_node, NodeType.SCHEMA_STRUCTURE, behavior_type_definition, 1)

        # Test the 'behavior' fields entry 1 type value
        behaviors_entry1_type_value_node = behaviors_entry1_type_node.children[0]
        _assert_structural_node(self, behaviors_entry1_type_value_node, NodeType.ENUM_VALUE, behavior_type_definition, 0)

        # Test the 'behavior' fields entry 1 input field
        behaviors_entry1_input_node = behaviors_entry1_node.children[4]
        _assert_structural_node(self, behaviors_entry1_input_node, NodeType.SCHEMA_STRUCTURE, field_definition, 1)

        # Test the 'behavior' fields entry 1 input field entry 1
        behaviors_entry1_input_entry1_node = behaviors_entry1_input_node.children[0]
        _assert_structural_node(self, behaviors_entry1_input_entry1_node, NodeType.LIST_ENTRY, None, 3)

        # Test the 'behavior' fields entry 1 input field entry 1 name
        behaviors_entry1_input_entry1_name_node = behaviors_entry1_input_entry1_node.children[0]
        _assert_structural_node(self, behaviors_entry1_input_entry1_name_node, NodeType.SCHEMA_STRUCTURE, primitives_definition, 1)

        # Test the 'behavior' fields entry 1 input field entry 1 name value
        behaviors_entry1_input_entry1_name_value_node = behaviors_entry1_input_entry1_name_node.children[0]
        _assert_structural_node(self, behaviors_entry1_input_entry1_name_value_node, NodeType.PRIMITIVE_VALUE, primitives_definition, 0)

        # Test the 'behavior' fields entry 1 acceptance field
        behaviors_entry1_acceptance_node = behaviors_entry1_node.children[6]
        _assert_structural_node(self, behaviors_entry1_acceptance_node, NodeType.SCHEMA_STRUCTURE, scenario_definition, 2)

        # Test the 'behavior' fields entry 1 acceptance field entry 1
        behaviors_entry1_acceptance_entry1_node = behaviors_entry1_acceptance_node.children[0]
        _assert_structural_node(self, behaviors_entry1_acceptance_entry1_node, NodeType.LIST_ENTRY, None, 5)

        # Test the 'behavior' fields entry 1 acceptance field entry 1 scenario
        behaviors_entry1_acceptance_entry1_scenario_node = behaviors_entry1_input_entry1_node.children[0]
        _assert_structural_node(self, behaviors_entry1_acceptance_entry1_scenario_node, NodeType.SCHEMA_STRUCTURE, primitives_definition, 1)

        # Test the 'behavior' fields entry 1 acceptance field entry 1 scenario value
        behaviors_entry1_acceptance_entry1_scenario_value_node = behaviors_entry1_acceptance_entry1_scenario_node.children[0]
        _assert_structural_node(self, behaviors_entry1_acceptance_entry1_scenario_value_node, NodeType.PRIMITIVE_VALUE, primitives_definition, 0)


def _assert_structural_node(test_case: TestCase, actual_node: StructuralNode, expected_node_type: NodeType, expected_defining_definition: Definition, expected_child_count: int):
    test_case.assertEqual(expected_node_type, actual_node.node_type)
    test_case.assertEqual(expected_defining_definition, actual_node.defining_definition)
    test_case.assertEqual(expected_child_count, len(actual_node.children))
