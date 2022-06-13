from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definition_by_name
from aac.lang.definitions.search import search_definition
from aac.plugins.plugin_manager import get_validator_plugins
from aac.validate import get_applicable_validators_for_definition
from aac.validate._collect_validators import _get_validation_entries, _get_validator_plugin_by_name

from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_enum_definition,
    create_field_entry,
    create_model_definition,
    create_validation_entry,
)


class TestCollectValidators(TestCase):
    def get_unique_validations(self, validations):
        return set([validation.get("name") for validation in validations])

    def test_get_applicable_validators_for_empty_schema_definition(self):
        test_definition = create_schema_definition("Empty Schema")
        active_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        schema_definition = active_context.get_definition_by_name("schema")
        field_definition = active_context.get_definition_by_name("Field")

        expected_schema_validations = search_definition(schema_definition, ["schema", "validation"])
        expected_field_validations = search_definition(field_definition, ["schema", "validation"])
        expected_validations = self.get_unique_validations(expected_schema_validations + expected_field_validations)
        actual_result = get_applicable_validators_for_definition(test_definition, validation_plugins, active_context)

        self.assertEqual(len(expected_validations), len(actual_result))

    def test_get_applicable_validators_for_schema_definition(self):
        test_field = create_field_entry("TestField", "string")
        test_definition = create_schema_definition("DataWithField", fields=[test_field])
        active_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        schema_definition = get_definition_by_name("schema", active_context.definitions)
        schema_validations = search_definition(schema_definition, ["schema", "validation"])
        field_definition = get_definition_by_name("Field", active_context.definitions)
        field_validations = search_definition(field_definition, ["schema", "validation"])

        expected_validations = self.get_unique_validations(schema_validations + field_validations)
        actual_result = get_applicable_validators_for_definition(test_definition, validation_plugins, active_context)

        self.assertEqual(len(expected_validations), len(actual_result))

    def test_get_applicable_validators_for_model_definition(self):
        test_field = create_field_entry("TestStateField", "string")
        test_definition = create_model_definition("ModelWithField", state=[test_field])
        active_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        schema_definition = get_definition_by_name("schema", active_context.definitions)
        schema_validations = search_definition(schema_definition, ["schema", "validation"])
        field_definition = get_definition_by_name("Field", active_context.definitions)
        field_validations = search_definition(field_definition, ["schema", "validation"])
        model_definition = get_definition_by_name("model", active_context.definitions)
        model_validations = search_definition(model_definition, ["schema", "validation"])

        expected_validations = self.get_unique_validations(schema_validations + field_validations + model_validations)
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

    def test_get_applicable_validators_for_definition_enum_returns_schema_validator(self):
        active_context = get_active_context(reload_context=True)

        validation_plugins = get_validator_plugins()

        enum_definition = create_enum_definition("Test Enum", ["val1", "val2"])
        schema_definition = get_definition_by_name("schema", active_context.definitions)

        expected_validations = search_definition(schema_definition, ["schema", "validation"])
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
        schema_definition_with_validation = create_schema_definition("name", validations=[validation1_entry, validation2_entry])

        expected_result = [validation1_entry, validation2_entry]
        actual_result = _get_validation_entries(schema_definition_with_validation)

        self.assertListEqual(expected_result, actual_result)

    def test__get_validator_plugin_by_name(self):

        validation_plugins = get_validator_plugins()

        self.assertGreater(len(validation_plugins), 0)

        first_validator_name = validation_plugins[0].name
        self.assertEqual(validation_plugins[0], _get_validator_plugin_by_name(first_validator_name, validation_plugins))

        second_validator_name = validation_plugins[1].name
        self.assertEqual(validation_plugins[1], _get_validator_plugin_by_name(second_validator_name, validation_plugins))
