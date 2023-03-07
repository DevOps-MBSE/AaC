from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.schema import get_definition_schema, get_root_schema_definitions, get_schema_defined_fields, get_definition_schema_components
from aac.lang.spec import get_root_fields

from tests.helpers.context import get_core_spec_context
from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_enum_definition,
    create_model_definition,
)


class TestDefinitionSchemas(TestCase):
    def test_get_root_schema_definitions_with_only_core_spec(self):
        test_context = get_core_spec_context()
        core_root_fields = get_root_fields()

        actual_results = get_root_schema_definitions(test_context)

        self.assertGreater(len(core_root_fields), 0)
        for root_field in core_root_fields:
            root_name = root_field.get("name")
            root_type = root_field.get("type")

            if test_context.is_definition_type(root_type):
                self.assertIn(root_name, actual_results)
            else:
                self.assertNotIn(root_name, actual_results)

    def test_get_root_schema_definitions_with_active_context(self):
        test_context = get_active_context()
        context_root_fields = test_context.get_root_fields()

        actual_results = get_root_schema_definitions(test_context)

        # Assert that the active context has at least the core spec set
        self.assertGreaterEqual(len(context_root_fields), len(get_root_fields()))

        for root_field in context_root_fields:
            root_name = root_field.get("name")
            root_type = root_field.get("type")

            if test_context.is_definition_type(root_type):
                self.assertIn(root_name, actual_results)
            else:
                self.assertNotIn(root_name, actual_results)

    def test_get_definition_root_schema_with_self_defined_data(self):
        test_context = get_core_spec_context()
        test_definition = test_context.get_definition_by_name("schema")

        expected_result = test_definition
        actual_result = get_definition_schema(test_definition, test_context)

        self.assertEqual(expected_result, actual_result)

    def test_get_definition_root_schema_with_user_defined_data(self):
        test_context = get_core_spec_context()
        test_definition = create_schema_definition("TestData")
        test_context.add_definition_to_context(test_definition)

        expected_result = test_context.get_definition_by_name("schema")
        actual_result = get_definition_schema(test_definition, test_context)

        self.assertEqual(expected_result, actual_result)

    def test_get_definition_root_schema_with_user_defined_model(self):
        test_context = get_core_spec_context()
        test_definition = create_model_definition("TestModel")
        test_context.add_definition_to_context(test_definition)

        expected_result = test_context.get_definition_by_name("model")
        actual_result = get_definition_schema(test_definition, test_context)

        self.assertEqual(expected_result, actual_result)

    def test_get_definition_root_schema_with_user_defined_enum(self):
        test_context = get_core_spec_context()
        test_definition = create_enum_definition("TestEnum", ["val1"])
        test_context.add_definition_to_context(test_definition)

        expected_result = test_context.get_definition_by_name("enum")
        actual_result = get_definition_schema(test_definition, test_context)

        self.assertEqual(expected_result, actual_result)

    def test_get_schema_defined_fields_with_user_defined_data(self):
        test_context = get_core_spec_context()
        test_definition = create_schema_definition("TestData")
        test_context.add_definition_to_context(test_definition)

        expected_fields = test_context.get_definition_by_name("schema").get_top_level_fields().get("fields")
        expected_result = {field.get("name"): field for field in expected_fields}
        actual_result = get_schema_defined_fields(test_definition, test_context)

        self.assertDictEqual(expected_result, actual_result)

    def test_get_schema_defined_fields_with_user_defined_model(self):
        test_context = get_core_spec_context()
        test_definition = create_model_definition("TestModel")
        test_context.add_definition_to_context(test_definition)

        expected_fields = test_context.get_definition_by_name("model").get_top_level_fields().get("fields")
        expected_result = {field.get("name"): field for field in expected_fields}
        actual_result = get_schema_defined_fields(test_definition, test_context)

        self.assertDictEqual(expected_result, actual_result)

    def test_get_definition_schema_components_with_data(self):
        test_context = get_core_spec_context()

        schema_definition = test_context.get_definition_by_name("schema")

        # Per the core spec, we'd expect DefinitionReference, Field, and ValidationReference
        field_definition = test_context.get_definition_by_name("Field")
        key_val_definition = test_context.get_definition_by_name("KeyValuePair")
        validation_reference_definition = test_context.get_definition_by_name("ValidationReference")
        definition_reference_definition = test_context.get_definition_by_name("DefinitionReference")

        expected_definitions = [definition_reference_definition, key_val_definition, field_definition, validation_reference_definition]
        actual_definitions = get_definition_schema_components(schema_definition, test_context)

        expected_definitions.sort()
        actual_definitions.sort()

        self.assertEqual(len(actual_definitions), 4)
        self.assertListEqual(expected_definitions, actual_definitions)

    def test_get_sub_definitions_with_model(self):
        test_context = get_core_spec_context()

        model_definition = create_model_definition("TestModel")
        test_context.add_definition_to_context(model_definition)

        # Per the core spec, we'd expect Field, Behavior, BehaviorType, and Scenario
        field_definition = test_context.get_definition_by_name("Field")
        component_field_definition = test_context.get_definition_by_name("ModelComponentField")
        behavior_definition = test_context.get_definition_by_name("Behavior")
        behavior_type_definition = test_context.get_definition_by_name("BehaviorType")
        scenario_definition = test_context.get_definition_by_name("Scenario")

        expected_definitions = [field_definition, component_field_definition, behavior_definition, behavior_type_definition, scenario_definition]
        actual_definitions = get_definition_schema_components(model_definition, test_context)
        expected_definitions.sort()
        actual_definitions.sort()

        # Per the core spec, we'd expect Field, ModelComponentField, Behavior, BehaviorType, and Scenario
        self.assertListEqual(actual_definitions, expected_definitions)
