from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definition_by_name, get_definitions_by_root_key
from aac.lang.definitions.definition import Definition
from aac.parser import parse
from aac.plugins.validators import ValidatorPlugin
from aac.plugins.validators.root_keys import get_plugin_aac_definitions, register_validators, validate_root_keys

from tests.helpers.assertion import assert_validator_result_success, assert_validator_result_failure
from tests.helpers.parsed_definitions import create_schema_definition, create_schema_ext_definition, create_field_entry


class TestRootKeysValidator(TestCase):
    def setUp(self) -> None:
        get_active_context(reload_context=True)

    def test_module_register_validators(self):
        actual_validator_plugin = register_validators()

        validation_definitions = get_definitions_by_root_key("validation", parse(get_plugin_aac_definitions()))
        self.assertEqual(1, len(validation_definitions))

        expected_validator_plugin = ValidatorPlugin(
            name="Root key is defined", definition=validation_definitions[0], validation_function=(lambda x: x)
        )
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugin.name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugin.definition)

    def test_validate_root_keys_valid_key(self):
        test_primitive_reference_field = create_field_entry("ValidPrimitiveField", "string")
        test_definition = create_schema_definition("TestData", [test_primitive_reference_field])

        test_active_context = get_active_context()
        test_active_context.add_definition_to_context(test_definition)

        target_schema_definition = get_definition_by_name("schema", test_active_context.definitions)
        actual_result = validate_root_keys(test_definition, target_schema_definition, test_active_context)

        assert_validator_result_success(actual_result)

    def test_validate_root_keys_invalid_key(self):
        fake_root_key = "not_a_root_key"
        test_definition_dict = {
            fake_root_key: {
                "name": "Test",
            }
        }
        test_definition = Definition("Test", "", "", [], test_definition_dict)

        test_active_context = get_active_context()
        test_active_context.add_definition_to_context(test_definition)

        target_schema_definition = test_active_context.get_definition_by_name(test_definition.get_root_key())
        actual_result = validate_root_keys(test_definition, target_schema_definition, test_active_context)

        assert_validator_result_failure(actual_result, "root", "key", fake_root_key)

    def test_validate_root_keys_valid_extended_root_key(self):
        fake_extended_root_key = "extended_root_key"
        test_definition_dict = {
            fake_extended_root_key: {
                "name": "Test",
            }
        }

        test_definition = Definition("Test", "", "", [], test_definition_dict)

        new_root_field = create_field_entry(fake_extended_root_key, fake_extended_root_key)
        root_key_extension = create_schema_ext_definition("NewRootKeys", "root", [new_root_field])
        test_active_context = get_active_context()
        test_active_context.add_definitions_to_context([test_definition, root_key_extension])

        target_schema_definition = get_definition_by_name("schema", test_active_context.definitions)
        actual_result = validate_root_keys(test_definition, target_schema_definition, test_active_context)

        assert_validator_result_success(actual_result)
