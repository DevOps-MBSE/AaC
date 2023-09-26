from unittest import TestCase
from aac.lang.constants import (
    BEHAVIOR_TYPE_REQUEST_RESPONSE,
    DEFINITION_FIELD_BEHAVIOR,
    DEFINITION_FIELD_INPUT,
    DEFINITION_FIELD_OUTPUT,
    DEFINITION_NAME_BEHAVIOR,
    DEFINITION_NAME_BEHAVIOR_TYPE,
    DEFINITION_NAME_FIELD,
    DEFINITION_NAME_REQUIREMENT_REFERENCE,
    DEFINITION_NAME_SCHEMA,
    DEFINITION_NAME_VALIDATION_REFERENCE,
    DEFINITION_NAME_SCENARIO,
    ROOT_KEY_MODEL,
)

from aac.lang.definitions.structure import get_substructures_by_type, strip_undefined_fields_from_definition, get_fields_by_enum_type
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

        field_definition = test_context.get_definition_by_name(DEFINITION_NAME_FIELD)
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
        test_component_entry = create_field_entry("TestComponent", sub_model_definition.name)
        test_model_definition = create_model_definition(
            "TestModel", components=[test_component_entry], behavior=[test_behavior_entry]
        )

        test_context.add_definitions_to_context([test_model_definition, sub_model_definition])

        scenario_definition = test_context.get_definition_by_name(DEFINITION_NAME_SCENARIO)
        field_definition = test_context.get_definition_by_name(DEFINITION_NAME_FIELD)
        behavior_definition = test_context.get_definition_by_name(DEFINITION_NAME_BEHAVIOR)

        expected_field_definitions = [test_input_field, test_component_entry]
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

        schema_definition = test_context.get_definition_by_name(DEFINITION_NAME_SCHEMA)

        field_definition = test_context.get_definition_by_name(DEFINITION_NAME_FIELD)
        validation_reference_definition = test_context.get_definition_by_name(DEFINITION_NAME_VALIDATION_REFERENCE)
        requirement_reference_requirement = test_context.get_definition_by_name(DEFINITION_NAME_REQUIREMENT_REFERENCE)

        expected_definitions = [
            field_definition,
            validation_reference_definition,
            requirement_reference_requirement,
        ]
        actual_definitions = get_definition_schema_components(schema_definition, test_context)

        self.assertListEqual(expected_definitions, actual_definitions)

    def test_get_definition_schema_components_with_model(self):
        test_context = get_core_spec_context()

        model_definition = create_model_definition("TestModel")
        test_context.add_definition_to_context(model_definition)

        field_definition = test_context.get_definition_by_name(DEFINITION_NAME_FIELD)
        behavior_definition = test_context.get_definition_by_name(DEFINITION_NAME_BEHAVIOR)
        behavior_type_definition = test_context.get_definition_by_name(DEFINITION_NAME_BEHAVIOR_TYPE)
        scenario_definition = test_context.get_definition_by_name(DEFINITION_NAME_SCENARIO)
        requirement_reference_definition = test_context.get_definition_by_name(DEFINITION_NAME_REQUIREMENT_REFERENCE)

        expected_definitions = [
            field_definition,
            behavior_definition,
            behavior_type_definition,
            scenario_definition,
            requirement_reference_definition,
        ]
        actual_definitions = get_definition_schema_components(model_definition, test_context)

        # Per the core spec, we'd expect Field, Behavior, BehaviorType, and Scenario
        self.assertEqual(len(actual_definitions), len(expected_definitions))
        for actual_definition in actual_definitions:
            self.assertIn(actual_definition, expected_definitions)

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

        test_model.structure[ROOT_KEY_MODEL][extra_top_level_field_name] = extra_top_level_field_value
        test_model.structure[ROOT_KEY_MODEL][DEFINITION_FIELD_BEHAVIOR][0][DEFINITION_FIELD_INPUT][0][
            behavior_input_extra_field_name
        ] = behavior_input_extra_field_value
        test_model.structure[ROOT_KEY_MODEL][DEFINITION_FIELD_BEHAVIOR][0][DEFINITION_FIELD_OUTPUT][0][
            behavior_output_extra_field_name
        ] = behavior_output_extra_field_value

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

    def test_get_fields_by_enum_type(self):
        test_context = get_core_spec_context()

        test_behavior_name = "TestBehavior"
        test_behavior_type = BEHAVIOR_TYPE_REQUEST_RESPONSE
        test_behavior = create_behavior_entry(test_behavior_name, test_behavior_type)
        test_model = create_model_definition("TestModel", behavior=[test_behavior])

        behavior_type_definition = test_context.get_definition_by_name(DEFINITION_NAME_BEHAVIOR_TYPE)

        enum_fields = get_fields_by_enum_type(test_model, behavior_type_definition, test_context)
        self.assertTrue(len(enum_fields))
