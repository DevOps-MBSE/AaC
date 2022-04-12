from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definition_by_name
from aac.lang.definitions.search import search_definition
from aac.plugins.plugin_manager import get_validator_plugins
from aac.validate import get_applicable_validators_for_definition
from aac.validate._collect_validators import _get_validation_entries, _get_validator_plugin_by_name

from tests.helpers.parsed_definitions import (
    create_data_definition,
    create_enum_definition,
    create_field_entry,
    create_model_definition,
    create_validation_entry,
)


class TestCollectValidators(TestCase):
    def test_get_applicable_validators_for_empty_data_definition(self):
        test_definition = create_data_definition("Empty Data")
        active_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        data_definition = active_context.get_definition_by_name("data")
        field_definition = active_context.get_definition_by_name("Field")

        expected_data_validations = search_definition(data_definition, ["data", "validation"])
        expected_field_validations = search_definition(field_definition, ["data", "validation"])
        expected_validations = expected_data_validations + expected_field_validations
        actual_result = get_applicable_validators_for_definition(test_definition, validation_plugins, active_context)

        self.assertEqual(len(expected_validations), len(actual_result))

    def test_get_applicable_validators_for_data_definition(self):
        test_field = create_field_entry("TestField", "string")
        test_definition = create_data_definition("DataWithField", fields=[test_field])
        active_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        data_definition = get_definition_by_name("data", active_context.definitions)
        data_validations = search_definition(data_definition, ["data", "validation"])
        field_definition = get_definition_by_name("Field", active_context.definitions)
        field_validations = search_definition(field_definition, ["data", "validation"])

        expected_validations = data_validations + field_validations
        actual_result = get_applicable_validators_for_definition(test_definition, validation_plugins, active_context)

        self.assertEqual(len(expected_validations), len(actual_result))

    def test_get_applicable_validators_for_model_definition(self):
        test_field = create_field_entry("TestStateField", "string")
        test_definition = create_model_definition("ModelWithField", state=[test_field])
        active_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        data_definition = get_definition_by_name("data", active_context.definitions)
        data_validations = search_definition(data_definition, ["data", "validation"])
        field_definition = get_definition_by_name("Field", active_context.definitions)
        field_validations = search_definition(field_definition, ["data", "validation"])

        expected_validations = data_validations + field_validations
        actual_result = get_applicable_validators_for_definition(test_definition, validation_plugins, active_context)

        self.assertEqual(len(expected_validations), len(actual_result))

    def test_get_applicable_validators_for_field_definition(self):
        target_definition_key = "Field"

        active_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        field_definition = get_definition_by_name(target_definition_key, active_context.definitions)

        expected_validations = field_definition.get_validations()
        actual_result = get_applicable_validators_for_definition(field_definition, validation_plugins, active_context)
        actual_plugin_names = [plugin.name for plugin in actual_result]

        self.assertGreater(len(actual_result), 0)
        for expected_validation in expected_validations:
            self.assertIn(expected_validation.get("name"), actual_plugin_names)

    def test_get_applicable_validators_for_definition_enum_returns_data_validator(self):
        active_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        enum_definition = create_enum_definition("Test Enum", ["val1", "val2"])
        data_definition = get_definition_by_name("data", active_context.definitions)

        expected_validations = search_definition(data_definition, ["data", "validation"])
        actual_result = get_applicable_validators_for_definition(enum_definition, validation_plugins, active_context)
        actual_plugin_names = [plugin.name for plugin in actual_result]

        self.assertGreater(len(actual_result), 0)
        for expected_validation in expected_validations:
            self.assertIn(expected_validation.get("name"), actual_plugin_names)

    def test__get_validation_entries(self):
        validation1_name = "Test Validation 1"
        validation2_name = "Test Validation 2"
        validation1_entry = create_validation_entry(validation1_name)
        validation2_entry = create_validation_entry(validation2_name)
        data_definition_with_validation = create_data_definition("name", validation=[validation1_entry, validation2_entry])

        expected_result = [validation1_entry, validation2_entry]
        actual_result = _get_validation_entries(data_definition_with_validation)

        self.assertListEqual(expected_result, actual_result)

    def test__get_validator_plugin_by_name(self):

        validation_plugins = get_validator_plugins()

        self.assertGreater(len(validation_plugins), 0)

        first_validator_name = validation_plugins[0].name
        self.assertEqual(validation_plugins[0], _get_validator_plugin_by_name(first_validator_name, validation_plugins))

        second_validator_name = validation_plugins[1].name
        self.assertEqual(validation_plugins[1], _get_validator_plugin_by_name(second_validator_name, validation_plugins))
