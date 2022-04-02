from unittest import TestCase
from aac.lang.context import LanguageContext

from aac.lang.definition_helpers import get_definition_by_name
from aac.lang.definitions.structure import get_sub_definitions, get_substructures_by_type

from tests.helpers.context import get_core_spec_context
from tests.helpers.parsed_definitions import (
    create_behavior_entry,
    create_data_definition,
    create_field_entry,
    create_model_definition,
    create_scenario_entry,
)


class TestDefinitionStructures(TestCase):
    def test_get_sub_definitions_with_data(self):
        test_context = get_core_spec_context()

        data_definition = get_definition_by_name("data", test_context.definitions)

        # Per the core spec, we'd expect Field and ValidationReference
        field_definition = get_definition_by_name("Field", test_context.definitions)
        validation_reference_definition = get_definition_by_name("ValidationReference", test_context.definitions)

        expected_definitions = [field_definition, validation_reference_definition]
        actual_definitions = get_sub_definitions(data_definition, test_context)

        self.assertEqual(len(actual_definitions), 2)
        self.assertListEqual(expected_definitions, actual_definitions)

    def test_get_sub_definitions_with_model(self):
        test_context = get_core_spec_context()

        model_definition = create_model_definition("TestModel")
        test_context.add_definition_to_context(model_definition)

        # Per the core spec, we'd expect Field, Behavior, BehaviorType, and Scenario
        field_definition = get_definition_by_name("Field", test_context.definitions)
        behavior_definition = get_definition_by_name("Behavior", test_context.definitions)
        behavior_type_definition = get_definition_by_name("BehaviorType", test_context.definitions)
        scenario_definition = get_definition_by_name("Scenario", test_context.definitions)

        expected_definitions = [field_definition, behavior_definition, behavior_type_definition, scenario_definition]
        actual_definitions = get_sub_definitions(model_definition, test_context)

        # Per the core spec, we'd expect Field, Behavior, BehaviorType, and Scenario
        self.assertEqual(len(actual_definitions), len(expected_definitions))
        for actual_definition in actual_definitions:
            self.assertIn(actual_definition, expected_definitions)

    def test_get_substructures_by_type_with_user_defined_data(self):
        test_context = get_core_spec_context()

        test_string_field_entry = create_field_entry("TestStringField", "string")
        test_file_field_entry = create_field_entry("TestFileField", "file")
        test_data_definition = create_data_definition(
            "TestData", fields=[test_string_field_entry, test_file_field_entry]
        )

        test_context.add_definition_to_context(test_data_definition)

        field_definition = test_context.get_definition_by_name("Field")
        expected_field_definitions = [test_string_field_entry, test_file_field_entry]

        actual_field_definitions = get_substructures_by_type(test_data_definition, field_definition, test_context)

        self.assertListEqual(expected_field_definitions, actual_field_definitions)

    def test_get_substructures_by_type_with_model(self):
        test_context = get_core_spec_context()

        sub_model_definition = create_model_definition("SubModel")

        test_input_field = create_field_entry("TestInput", "string")
        test_acceptance_field = create_scenario_entry("TestScenario")
        test_behavior_entry = create_behavior_entry("TestBehavior", input=[test_input_field], acceptance=[test_acceptance_field])
        test_component_entry = create_field_entry("TestComponent", sub_model_definition.name)
        test_model_definition = create_model_definition(
            "TestModel", components=[test_component_entry], behavior=[test_behavior_entry]
        )

        test_context.add_definitions_to_context([test_model_definition, sub_model_definition])

        scenario_definition = test_context.get_definition_by_name("Scenario")
        field_definition = test_context.get_definition_by_name("Field")
        behavior_definition = test_context.get_definition_by_name("Behavior")

        expected_field_definitions = [test_component_entry, test_input_field]
        expected_behavior_definitions = [test_behavior_entry]
        expected_scenario_definitions = [test_acceptance_field]

        actual_field_definitions = get_substructures_by_type(test_model_definition, field_definition, test_context)
        actual_behavior_definitions = get_substructures_by_type(test_model_definition, behavior_definition, test_context)
        actual_scenario_definitions = get_substructures_by_type(test_model_definition, scenario_definition, test_context)

        self.assertListEqual(expected_field_definitions, actual_field_definitions)
        self.assertListEqual(expected_behavior_definitions, actual_behavior_definitions)
        self.assertListEqual(expected_scenario_definitions, actual_scenario_definitions)
