from unittest import TestCase

from aac.lang.definitions.structure import get_substructures_by_type, strip_undefined_fields_from_definition
from aac.lang.definitions.schema import get_definition_schema_components

from tests.helpers.context import get_core_spec_context
from tests.helpers.parsed_definitions import (
    create_behavior_entry,
    create_schema_definition,
    create_field_entry,
    create_model_definition,
    create_scenario_entry,
)


class TestDefinitionStructures(TestCase):

    def test_get_substructures_by_type_with_user_defined_data(self):
        test_context = get_core_spec_context()

        test_string_field_entry = create_field_entry("TestStringField", "string")
        test_file_field_entry = create_field_entry("TestFileField", "file")
        test_schema_definition = create_schema_definition("TestData", fields=[test_string_field_entry, test_file_field_entry])

        test_context.add_definition_to_context(test_schema_definition)

        field_definition = test_context.get_definition_by_name("Field")
        expected_field_definitions = [test_string_field_entry, test_file_field_entry]

        actual_field_definitions = get_substructures_by_type(test_schema_definition, field_definition, test_context)

        self.assertListEqual(expected_field_definitions, actual_field_definitions)

    def test_get_substructures_by_type_with_model(self):
        test_context = get_core_spec_context()

        sub_model_definition = create_model_definition("SubModel")

        test_input_field = create_field_entry("TestInput", "string")
        test_acceptance_field = create_scenario_entry("TestScenario")
        test_behavior_entry = create_behavior_entry(
            "TestBehavior", input=[test_input_field], acceptance=[test_acceptance_field]
        )
        test_model_definition = create_model_definition(
            "TestModel", behavior=[test_behavior_entry]
        )

        test_context.add_definitions_to_context([test_model_definition, sub_model_definition])

        scenario_definition = test_context.get_definition_by_name("Scenario")
        field_definition = test_context.get_definition_by_name("Field")
        behavior_definition = test_context.get_definition_by_name("Behavior")

        expected_field_definitions = [test_input_field]
        expected_behavior_definitions = [test_behavior_entry]
        expected_scenario_definitions = [test_acceptance_field]

        actual_field_definitions = get_substructures_by_type(test_model_definition, field_definition, test_context)
        actual_behavior_definitions = get_substructures_by_type(test_model_definition, behavior_definition, test_context)
        actual_scenario_definitions = get_substructures_by_type(test_model_definition, scenario_definition, test_context)

        self.assertListEqual(expected_field_definitions, actual_field_definitions)
        self.assertListEqual(expected_behavior_definitions, actual_behavior_definitions)
        self.assertListEqual(expected_scenario_definitions, actual_scenario_definitions)

    def test_get_definition_schema_components_with_data(self):
        test_context = get_core_spec_context()

        schema_definition = test_context.get_definition_by_name("schema")

        # Per the core spec, we'd expect DefinitionReference, Field, and ValidationReference
        field_definition = test_context.get_definition_by_name("Field")
        validation_reference_definition = test_context.get_definition_by_name("ValidationReference")
        definition_reference_definition = test_context.get_definition_by_name("DefinitionReference")
        key_value_reference_definition = test_context.get_definition_by_name("KeyValuePair")

        expected_definitions = [definition_reference_definition, field_definition, validation_reference_definition, key_value_reference_definition]
        actual_definitions = get_definition_schema_components(schema_definition, test_context)

        self.assertEqual(len(actual_definitions), 4)
        self.assertListEqual(expected_definitions, actual_definitions)

    def test_get_definition_schema_components_with_model(self):
        test_context = get_core_spec_context()

        model_definition = create_model_definition("TestModel")
        test_context.add_definition_to_context(model_definition)

        # Per the core spec, we'd expect Field, ModelComponentField, Behavior, BehaviorType, and Scenario
        field_definition = test_context.get_definition_by_name("Field")
        component_field_definition = test_context.get_definition_by_name("ModelComponentField")
        behavior_definition = test_context.get_definition_by_name("Behavior")
        behavior_type_definition = test_context.get_definition_by_name("BehaviorType")
        scenario_definition = test_context.get_definition_by_name("Scenario")

        expected_definitions = [field_definition, component_field_definition, behavior_definition, behavior_type_definition, scenario_definition]
        actual_definitions = get_definition_schema_components(model_definition, test_context)
        expected_definitions.sort()
        actual_definitions.sort()

        # Per the core spec, we'd expect Field, Behavior, BehaviorType, and Scenario
        self.assertListEqual(actual_definitions, expected_definitions)

    def test_strip_undefined_fields_from_definition(self):
        test_context = get_core_spec_context()
        self.maxDiff = None

        behavior_input = create_field_entry("BehaviorOutput")
        behavior_output = create_field_entry("BehaviorInput")
        model_behavior = create_behavior_entry("SomeBehavior", input=[behavior_input], output=[behavior_output])
        model_component = create_field_entry("ModelComponent", "ModelComponent")
        test_model = create_model_definition("ModelWithExtraFields", components=[model_component], behavior=[model_behavior])

        expected_result = test_model.copy()

        extra_top_level_field_name = "extra_top_level_field_name"
        extra_top_level_field_value = "extra_top_level_field_value"

        behavior_input_extra_field_name = "behavior_input_extra_field_name"
        behavior_input_extra_field_value = "behavior_input_extra_field_value"

        behavior_output_extra_field_name = "behavior_output_extra_field_name"
        behavior_output_extra_field_value = "behavior_output_extra_field_value"

        test_model.structure["model"][extra_top_level_field_name] = extra_top_level_field_value
        test_model.structure["model"]["behavior"][0]["input"][0][behavior_input_extra_field_name] = behavior_input_extra_field_value
        test_model.structure["model"]["behavior"][0]["output"][0][behavior_output_extra_field_name] = behavior_output_extra_field_value

        actual_result = strip_undefined_fields_from_definition(test_model, test_context)
        actual_result_yaml_dump = actual_result.to_yaml()

        self.assertNotEqual(expected_result.to_yaml(), test_model.to_yaml())
        self.assertDictEqual(expected_result.structure, actual_result.structure)

        self.assertNotIn(extra_top_level_field_name, actual_result_yaml_dump)
        self.assertNotIn(extra_top_level_field_value, actual_result_yaml_dump)
        self.assertNotIn(behavior_input_extra_field_name, actual_result_yaml_dump)
        self.assertNotIn(behavior_input_extra_field_value, actual_result_yaml_dump)
        self.assertNotIn(behavior_output_extra_field_name, actual_result_yaml_dump)
        self.assertNotIn(behavior_output_extra_field_value, actual_result_yaml_dump)
