from unittest import TestCase

from aac.lang.context_manager import get_active_context
from aac.lang.definition_helpers import get_definition_by_name, get_definitions_by_root_key
from aac.parser import parse
from aac.plugins.validators import ValidatorPlugin, ValidatorResult
from aac.plugins.validators.required_fields import get_plugin_aac_definitions, register_validators, validate_required_fields

from tests.helpers.parsed_definitions import create_data_definition, create_field_entry

TEST_IMPLEMENTING_DEFINITION_NAME = "TestDefinitionWhichImplementsTheRequiredFieldsDefinition"
TEST_IMPLEMENTING_DEFINITION_FIELD_NAME = "field_name"
TEST_SCHEMA_DEFINITION_NAME = "TestDefinitionWithRequiredFields"
TEST_DEFINITION_FIELD_NAME = "DefinitionField"
TEST_DEFINITION_ARRAY_FIELD_NAME = "DefinitionArrayField"
TEST_PRIMITIVE_FIELD_NAME = "PrimitiveField"
TEST_PRIMITIVE_ARRAY_FIELD_NAME = "PrimitiveArrayField"


class TestDefinedReferencesPlugin(TestCase):
    def setUp(self) -> None:
        get_active_context(reload_context=True)

    def test_module_register_validators(self):
        actual_validator_plugin = register_validators()

        validation_definitions = get_definitions_by_root_key("validation", parse(get_plugin_aac_definitions()))
        self.assertEqual(1, len(validation_definitions))

        expected_validator_plugin = ValidatorPlugin(
            name="Required fields are present", definition=validation_definitions[0], validation_function=(lambda x: x)
        )
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugin.name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugin.definition)

    def test_validate_validate_required_fields_no_missing_required_fields(self):
        test_active_context = get_active_context(reload_context=True)

        test_field_entry = create_field_entry("TestField", "string")
        test_data_definition = create_data_definition("TestData", [test_field_entry])
        required_fields_definition = get_definition_by_name("data", test_active_context.definitions)

        expected_result = ValidatorResult([], True)

        actual_result = validate_required_fields(test_data_definition, required_fields_definition, test_active_context)

        self.assertEqual(expected_result, actual_result)

    def test_validate_required_fields_with_missing_name_empty_fields(self):
        test_active_context = get_active_context(reload_context=True)

        test_data_definition = create_data_definition("TestData")
        del test_data_definition.structure["data"]["name"]

        required_fields_definition = get_definition_by_name("data", test_active_context.definitions)

        expected_result = ValidatorResult(["required", "missing"], False)

        actual_result = validate_required_fields(test_data_definition, required_fields_definition, test_active_context)

        self.assertEqual(expected_result.is_valid, actual_result.is_valid)
        self.assertEqual(len(expected_result.messages), len(actual_result.messages))
        actual_result_message = actual_result.get_messages_as_string()

        self.assertIn("name", actual_result_message)
        self.assertIn("missing", actual_result_message)
        self.assertIn("field", actual_result_message)
        self.assertIn("populated", actual_result_message)
