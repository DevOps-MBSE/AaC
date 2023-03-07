from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.collections import get_definition_by_name
from aac.lang.constants import DEFINITION_NAME_FIELD, DEFINITION_NAME_MODEL, DEFINITION_NAME_SCHEMA, DEFINITION_FIELD_NAME, PRIMITIVE_TYPE_STRING
from aac.validate import get_applicable_validators_for_definition
from aac.validate._collect_validators import _get_validation_entries, _get_validator_plugin_by_name

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_enum_definition,
    create_field_entry,
    create_model_definition,
    create_validation_entry,
)


class TestCollectValidators(ActiveContextTestCase):
    def get_unique_validations(self, validations):
        return set([validation.get(DEFINITION_FIELD_NAME) for validation in validations])

    def test_get_applicable_validators_for_schema_definition(self):
        test_field = create_field_entry("TestField", PRIMITIVE_TYPE_STRING)
        test_definition = create_schema_definition("DataWithField", fields=[test_field])
        active_context = get_active_context()

        validation_plugins = active_context.get_definition_validations()

        # get validations from types we know to have assigned validators
        expected_validations = self.get_unique_validations(
            active_context.get_definition_by_name(DEFINITION_NAME_SCHEMA).get_validations()
            + active_context.get_definition_by_name(DEFINITION_NAME_FIELD).get_validations()
            + active_context.get_definition_by_name("Requirement").get_validations())

        actual_result = get_applicable_validators_for_definition(test_definition, validation_plugins, active_context)

        self.assertEqual(len(expected_validations), len(actual_result))

    def test_get_applicable_validators_for_model_definition(self):
        test_field = create_field_entry("TestStateField", PRIMITIVE_TYPE_STRING)
        test_definition = create_model_definition("ModelWithField", state=[test_field])
        active_context = get_active_context()

        validation_plugins = active_context.get_definition_validations()

        # get validations from types we know to have assigned validators
        expected_validations = self.get_unique_validations(
            active_context.get_definition_by_name(DEFINITION_NAME_SCHEMA).get_validations()
            + active_context.get_definition_by_name(DEFINITION_NAME_FIELD).get_validations()
            + active_context.get_definition_by_name(DEFINITION_NAME_MODEL).get_validations()
            + active_context.get_definition_by_name("ModelComponentField").get_validations()
            + active_context.get_definition_by_name("Requirement").get_validations())

        actual_result = get_applicable_validators_for_definition(test_definition, validation_plugins, active_context)

        self.assertEqual(len(expected_validations), len(actual_result))

    def test_get_applicable_validators_for_field_definition(self):
        target_definition_key = DEFINITION_NAME_FIELD

        active_context = get_active_context()

        validation_plugins = active_context.get_definition_validations()

        field_definition = get_definition_by_name(target_definition_key, active_context.definitions)

        expected_validations = field_definition.get_validations()
        actual_result = get_applicable_validators_for_definition(field_definition, validation_plugins, active_context)
        actual_plugin_names = [plugin.name for plugin in actual_result]

        self.assertGreater(len(actual_result), 0)
        for expected_validation in expected_validations:
            self.assertIn(expected_validation.get(DEFINITION_FIELD_NAME), actual_plugin_names)

    def test_get_applicable_validators_for_definition_enum_returns_schema_validator(self):
        active_context = get_active_context()

        validation_plugins = active_context.get_definition_validations()

        enum_definition = create_enum_definition("Test Enum", ["val1", "val2"])
        schema_definition = get_definition_by_name(DEFINITION_NAME_SCHEMA, active_context.definitions)

        actual_result = get_applicable_validators_for_definition(enum_definition, validation_plugins, active_context)
        actual_plugin_names = [plugin.name for plugin in actual_result]

        self.assertGreater(len(actual_result), 0)
        for expected_validation in schema_definition.get_validations():
            self.assertIn(expected_validation.get(DEFINITION_FIELD_NAME), actual_plugin_names)

    def test__get_validation_entries(self):
        validation1_name = "Test Validation 1"
        validation2_name = "Test Validation 2"
        validation1_entry = create_validation_entry(validation1_name)
        validation2_entry = create_validation_entry(validation2_name)
        schema_definition_with_validation = create_schema_definition(DEFINITION_FIELD_NAME, validations=[validation1_entry, validation2_entry])

        expected_result = [validation1_entry, validation2_entry]
        actual_result = _get_validation_entries(schema_definition_with_validation)

        self.assertListEqual(expected_result, actual_result)

    def test__get_validator_plugin_by_name(self):
        active_context = get_active_context()
        validation_plugins = active_context.get_definition_validations()

        self.assertGreater(len(validation_plugins), 0)

        first_validator_name = validation_plugins[0].name
        self.assertEqual(validation_plugins[0], _get_validator_plugin_by_name(first_validator_name, validation_plugins))

        second_validator_name = validation_plugins[1].name
        self.assertEqual(validation_plugins[1], _get_validator_plugin_by_name(second_validator_name, validation_plugins))
