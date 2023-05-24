from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import (
    DEFINITION_FIELD_ACCEPTANCE,
    DEFINITION_FIELD_BEHAVIOR,
    DEFINITION_FIELD_COMPONENTS,
    DEFINITION_FIELD_DESCRIPTION,
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_GIVEN,
    DEFINITION_FIELD_INPUT,
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_OUTPUT,
    DEFINITION_FIELD_SCENARIO,
    DEFINITION_FIELD_STATE,
    DEFINITION_FIELD_TAGS,
    DEFINITION_FIELD_THEN,
    DEFINITION_FIELD_TYPE,
    DEFINITION_FIELD_WHEN,
    DEFINITION_NAME_BEHAVIOR,
    DEFINITION_NAME_BEHAVIOR_TYPE,
    DEFINITION_NAME_DEFINITION_REFERENCE,
    DEFINITION_NAME_FIELD,
    DEFINITION_NAME_MODEL,
    DEFINITION_NAME_PRIMITIVES,
    DEFINITION_NAME_REQUIREMENT_REFERENCE,
    DEFINITION_NAME_SCENARIO,
    DEFINITION_NAME_VALIDATION_REFERENCE,
    ROOT_KEY_ENUM,
    ROOT_KEY_MODEL,
    ROOT_KEY_SCHEMA,
)
from aac.lang.definitions.schema import (
    get_definition_schema,
    get_root_schema_definitions,
    get_schema_defined_fields,
    get_definition_schema_components,
    get_schema_for_field,
)
from aac.spec import get_root_fields

from tests.helpers.context import get_core_spec_context
from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_enum_definition,
    create_model_definition,
)
from tests.helpers.prebuilt_definition_constants import TEST_SERVICE_ONE


class TestDefinitionSchemas(TestCase):
    def test_get_root_schema_definitions_with_only_core_spec(self):
        test_context = get_core_spec_context()
        core_root_fields = get_root_fields()

        actual_results = get_root_schema_definitions(test_context)

        self.assertGreater(len(core_root_fields), 0)
        for root_field in core_root_fields:
            root_name = root_field.get(DEFINITION_FIELD_NAME)
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
            root_name = root_field.get(DEFINITION_FIELD_NAME)
            root_type = root_field.get("type")

            if test_context.is_definition_type(root_type):
                self.assertIn(root_name, actual_results)
            else:
                self.assertNotIn(root_name, actual_results)

    def test_get_definition_root_schema_with_self_defined_data(self):
        test_context = get_core_spec_context()
        test_definition = test_context.get_definition_by_name(ROOT_KEY_SCHEMA)

        expected_result = test_definition
        actual_result = get_definition_schema(test_definition, test_context)

        self.assertEqual(expected_result, actual_result)

    def test_get_definition_root_schema_with_user_defined_data(self):
        test_context = get_core_spec_context()
        test_definition = create_schema_definition("TestData")
        test_context.add_definition_to_context(test_definition)

        expected_result = test_context.get_definition_by_name(ROOT_KEY_SCHEMA)
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

        expected_result = test_context.get_definition_by_name(ROOT_KEY_ENUM)
        actual_result = get_definition_schema(test_definition, test_context)

        self.assertEqual(expected_result, actual_result)

    def test_get_schema_defined_fields_with_user_defined_data(self):
        test_context = get_core_spec_context()
        test_definition = create_schema_definition("TestData")
        test_context.add_definition_to_context(test_definition)

        expected_fields = (
            test_context.get_definition_by_name(ROOT_KEY_SCHEMA).get_top_level_fields().get(DEFINITION_FIELD_FIELDS)
        )
        expected_result = {field.get(DEFINITION_FIELD_NAME): field for field in expected_fields}
        actual_result = get_schema_defined_fields(test_definition, test_context)

        self.assertDictEqual(expected_result, actual_result)

    def test_get_schema_defined_fields_with_user_defined_model(self):
        test_context = get_core_spec_context()
        test_definition = create_model_definition("TestModel")
        test_context.add_definition_to_context(test_definition)

        expected_fields = (
            test_context.get_definition_by_name(ROOT_KEY_MODEL).get_top_level_fields().get(DEFINITION_FIELD_FIELDS)
        )
        expected_result = {field.get(DEFINITION_FIELD_NAME): field for field in expected_fields}
        actual_result = get_schema_defined_fields(test_definition, test_context)

        self.assertDictEqual(expected_result, actual_result)

    def test_get_definition_schema_components_with_data(self):
        test_context = get_core_spec_context()

        schema_definition = test_context.get_definition_by_name(ROOT_KEY_SCHEMA)

        field_definition = test_context.get_definition_by_name(DEFINITION_NAME_FIELD)
        validation_reference_definition = test_context.get_definition_by_name(DEFINITION_NAME_VALIDATION_REFERENCE)
        definition_reference_definition = test_context.get_definition_by_name(DEFINITION_NAME_DEFINITION_REFERENCE)
        requirement_reference_definition = test_context.get_definition_by_name(DEFINITION_NAME_REQUIREMENT_REFERENCE)

        expected_definitions = [
            definition_reference_definition,
            field_definition,
            validation_reference_definition,
            requirement_reference_definition,
        ]
        actual_definitions = get_definition_schema_components(schema_definition, test_context)

        self.assertListEqual(expected_definitions, actual_definitions)

    def test_get_sub_definitions_with_model(self):
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

        self.assertEqual(len(actual_definitions), len(expected_definitions))
        for actual_definition in actual_definitions:
            self.assertIn(actual_definition, expected_definitions)

    def test_get_schema_for_fields(self):
        test_context = get_core_spec_context()
        test_definition = TEST_SERVICE_ONE.copy()

        def _test_get_schema_for_field(keys, expected):
            field_schema = get_schema_for_field(test_definition, keys, test_context)
            self.assertEqual(expected, field_schema)

        model_definition = test_context.get_definition_by_name(DEFINITION_NAME_MODEL)
        primitives_definition = test_context.get_definition_by_name(DEFINITION_NAME_PRIMITIVES)
        field_definition = test_context.get_definition_by_name(DEFINITION_NAME_FIELD)
        behavior_definition = test_context.get_definition_by_name(DEFINITION_NAME_BEHAVIOR)
        behavior_type_definition = test_context.get_definition_by_name(DEFINITION_NAME_BEHAVIOR_TYPE)
        scenario_definition = test_context.get_definition_by_name(DEFINITION_NAME_SCENARIO)

        # prepared key lists for brevity
        model_keys = [DEFINITION_NAME_MODEL]
        model_behavior_keys = [DEFINITION_NAME_MODEL, DEFINITION_FIELD_BEHAVIOR]
        model_behavior_acceptance_keys = [DEFINITION_NAME_MODEL, DEFINITION_FIELD_BEHAVIOR, DEFINITION_FIELD_ACCEPTANCE]

        test_cases = [
            ([*model_keys], model_definition),
            ([*model_keys, DEFINITION_FIELD_NAME], primitives_definition),
            ([*model_keys, DEFINITION_FIELD_DESCRIPTION], primitives_definition),
            ([*model_keys, DEFINITION_FIELD_COMPONENTS], field_definition),
            ([*model_keys, DEFINITION_FIELD_BEHAVIOR], behavior_definition),
            ([*model_keys, DEFINITION_FIELD_STATE], field_definition),
            ([*model_behavior_keys, DEFINITION_FIELD_NAME], primitives_definition),
            ([*model_behavior_keys, DEFINITION_FIELD_TYPE], behavior_type_definition),
            ([*model_behavior_keys, DEFINITION_FIELD_DESCRIPTION], primitives_definition),
            ([*model_behavior_keys, DEFINITION_FIELD_TAGS], primitives_definition),
            ([*model_behavior_keys, DEFINITION_FIELD_INPUT], field_definition),
            ([*model_behavior_keys, DEFINITION_FIELD_INPUT, DEFINITION_FIELD_NAME], primitives_definition),
            ([*model_behavior_keys, DEFINITION_FIELD_INPUT, DEFINITION_FIELD_TYPE], primitives_definition),
            ([*model_behavior_keys, DEFINITION_FIELD_INPUT, DEFINITION_FIELD_DESCRIPTION], primitives_definition),
            ([*model_behavior_keys, DEFINITION_FIELD_OUTPUT], field_definition),
            ([*model_behavior_acceptance_keys], scenario_definition),
            ([*model_behavior_acceptance_keys, DEFINITION_FIELD_SCENARIO], primitives_definition),
            ([*model_behavior_acceptance_keys, DEFINITION_FIELD_TAGS], primitives_definition),
            ([*model_behavior_acceptance_keys, DEFINITION_FIELD_GIVEN], primitives_definition),
            ([*model_behavior_acceptance_keys, DEFINITION_FIELD_WHEN], primitives_definition),
            ([*model_behavior_acceptance_keys, DEFINITION_FIELD_THEN], primitives_definition),
        ]

        for test_keys, expected in test_cases:
            _test_get_schema_for_field(test_keys, expected)
