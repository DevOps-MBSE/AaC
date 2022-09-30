from unittest import TestCase
from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.definitions.inheritance import get_inherited_attributes, apply_inherited_attributes_to_definition
from aac.plugins.validators import required_fields
from aac.plugins.validators import defined_references

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_schema_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
    create_validation_entry,
)


class TestDefinitionInheritance(TestCase):

    def test_get_inherited_attributes(self):
        test_context = get_initialized_language_context()
        test_context.add_definitions_to_context([TEST_SCHEMA_PARENT_1, TEST_SCHEMA_PARENT_2, TEST_SCHEMA_CHILD])

        actual_results = get_inherited_attributes(TEST_SCHEMA_CHILD, test_context)
        self.assertIsNotNone(actual_results)
        self.assertIn(TEST_SCHEMA_PARENT_1_NAME, actual_results)
        self.assertIn("fields", actual_results.get(TEST_SCHEMA_PARENT_1_NAME))
        self.assertIn("validations", actual_results.get(TEST_SCHEMA_PARENT_1_NAME))
        self.assertIn("fields", actual_results.get(TEST_SCHEMA_PARENT_1_NAME))

        self.assertIn(TEST_SCHEMA_PARENT_2_NAME, actual_results)

    def test_apply_inherited_attributes_to_definition_with_fully_loaded_parents(self):
        test_context = get_initialized_language_context()
        test_child_definition = TEST_SCHEMA_CHILD.copy()
        test_context.add_definitions_to_context([TEST_SCHEMA_PARENT_1, TEST_SCHEMA_PARENT_2, test_child_definition])

        apply_inherited_attributes_to_definition(test_child_definition, test_context)
        actual_validations = test_child_definition.get_validations()
        actual_fields = test_child_definition.get_top_level_fields().get("fields")

        self.assertEqual(len(actual_validations), 2)
        field_names = [field.get("name") for field in actual_fields]
        self.assertIn(TEST_SCHEMA_PARENT_1_FIELD_NAME, field_names)
        self.assertIn(TEST_SCHEMA_PARENT_2_FIELD_NAME, field_names)
        self.assertIn(TEST_SCHEMA_CHILD_FIELD_NAME, field_names)

        field_types = [field.get("type") for field in actual_fields]
        self.assertIn(TEST_SCHEMA_PARENT_1_FIELD_TYPE, field_types)
        self.assertIn(TEST_SCHEMA_PARENT_2_FIELD_TYPE, field_types)
        self.assertIn(TEST_SCHEMA_CHILD_FIELD_TYPE, field_types)

        validation_names = [validation.get("name") for validation in actual_validations]
        self.assertIn(TEST_SCHEMA_PARENT_1_VALIDATION_NAME, validation_names)
        self.assertIn(TEST_SCHEMA_PARENT_2_VALIDATION_NAME, validation_names)

    def test_apply_inherited_attributes_to_definition_with_partial_parents(self):
        test_context = get_initialized_language_context()
        test_parent_1_definition = TEST_SCHEMA_PARENT_1.copy()
        test_parent_2_definition = TEST_SCHEMA_PARENT_2.copy()

        del test_parent_1_definition.get_top_level_fields()["validation"]
        del test_parent_2_definition.get_top_level_fields()["fields"]

        test_child_definition = TEST_SCHEMA_CHILD.copy()
        test_context.add_definitions_to_context([test_parent_1_definition, test_parent_2_definition, test_child_definition])

        apply_inherited_attributes_to_definition(test_child_definition, test_context)
        actual_validations = test_child_definition.get_validations()
        actual_fields = test_child_definition.get_top_level_fields().get("fields")

        field_names = [field.get("name") for field in actual_fields]
        self.assertIn(TEST_SCHEMA_PARENT_1_FIELD_NAME, field_names)
        self.assertNotIn(TEST_SCHEMA_PARENT_2_FIELD_NAME, field_names)
        self.assertIn(TEST_SCHEMA_CHILD_FIELD_NAME, field_names)

        field_types = [field.get("type") for field in actual_fields]
        self.assertIn(TEST_SCHEMA_PARENT_1_FIELD_TYPE, field_types)
        self.assertIn(TEST_SCHEMA_CHILD_FIELD_TYPE, field_types)

        validation_names = [validation.get("name") for validation in actual_validations]
        self.assertNotIn(TEST_SCHEMA_PARENT_1_VALIDATION_NAME, validation_names)
        self.assertIn(TEST_SCHEMA_PARENT_2_VALIDATION_NAME, validation_names)


TEST_SCHEMA_PARENT_1_NAME = "Parent1"
TEST_SCHEMA_PARENT_1_FIELD_NAME = "P1F1"
TEST_SCHEMA_PARENT_1_FIELD_TYPE = "integer"
TEST_SCHEMA_PARENT_1_FIELD = create_field_entry(TEST_SCHEMA_PARENT_1_FIELD_NAME, TEST_SCHEMA_PARENT_1_FIELD_TYPE)
TEST_SCHEMA_PARENT_1_VALIDATION_NAME = required_fields.PLUGIN_NAME
TEST_SCHEMA_PARENT_1 = create_schema_definition(TEST_SCHEMA_PARENT_1_NAME, fields=[TEST_SCHEMA_PARENT_1_FIELD], validations=[TEST_SCHEMA_PARENT_1_VALIDATION_NAME])

TEST_SCHEMA_PARENT_2_NAME = "Parent2"
TEST_SCHEMA_PARENT_2_FIELD_NAME = "P2F1"
TEST_SCHEMA_PARENT_2_FIELD_TYPE = "string"
TEST_SCHEMA_PARENT_2_FIELD = create_field_entry(TEST_SCHEMA_PARENT_2_FIELD_NAME, TEST_SCHEMA_PARENT_2_FIELD_TYPE)
TEST_SCHEMA_PARENT_2_VALIDATION_NAME = defined_references.PLUGIN_NAME
TEST_SCHEMA_PARENT_2_VALIDATION = create_validation_entry(TEST_SCHEMA_PARENT_2_VALIDATION_NAME, [TEST_SCHEMA_PARENT_2_FIELD_NAME])
TEST_SCHEMA_PARENT_2 = create_schema_definition(TEST_SCHEMA_PARENT_2_NAME, fields=[TEST_SCHEMA_PARENT_2_FIELD], validations=[TEST_SCHEMA_PARENT_2_VALIDATION])

TEST_SCHEMA_CHILD_NAME = "Child"
TEST_SCHEMA_CHILD_FIELD_NAME = "ChildField1"
TEST_SCHEMA_CHILD_FIELD_TYPE = "string"
TEST_SCHEMA_CHILD_FIELD = create_field_entry(TEST_SCHEMA_CHILD_FIELD_NAME, TEST_SCHEMA_CHILD_FIELD_TYPE)
TEST_SCHEMA_CHILD_VALIDATION_NAME = defined_references.PLUGIN_NAME
TEST_SCHEMA_CHILD_VALIDATION = create_validation_entry(TEST_SCHEMA_CHILD_VALIDATION_NAME, [TEST_SCHEMA_CHILD_FIELD_NAME])
TEST_SCHEMA_CHILD = create_schema_definition(TEST_SCHEMA_CHILD_NAME, fields=[TEST_SCHEMA_CHILD_FIELD], inherits=[TEST_SCHEMA_PARENT_1_NAME, TEST_SCHEMA_PARENT_2_NAME])
