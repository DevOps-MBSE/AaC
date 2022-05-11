from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definitions_by_root_key
from aac.parser import parse
from aac.plugins.validators import ValidatorPlugin
from aac.plugins.validators.required_fields import get_plugin_aac_definitions, register_validators, validate_required_fields
from tests.helpers.assertion import assert_validator_result_failure, assert_validator_result_success

from tests.helpers.parsed_definitions import create_behavior_entry, create_schema_definition, create_field_entry, create_model_definition


class TestRequiredFieldsPlugin(TestCase):
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

    def test_validate_required_fields_not_missing_required_fields_for_schema_definition(self):
        test_active_context = get_active_context(reload_context=True)

        test_field_entry = create_field_entry("TestField", "string")
        test_definition = create_schema_definition("TestData", [test_field_entry])

        required_fields_definition = test_active_context.get_definition_by_name(test_definition.get_root_key())
        actual_result = validate_required_fields(test_definition, required_fields_definition, test_active_context)

        assert_validator_result_success(actual_result)

    def test_validate_required_fields_no_missing_required_fields_for_model_definition(self):
        test_active_context = get_active_context(reload_context=True)

        test_behavior_entry = create_behavior_entry("TestBehavior")
        test_model_definition = create_model_definition("TestModel", behavior=[test_behavior_entry])

        required_fields_definition = test_active_context.get_definition_by_name(test_model_definition.get_root_key())
        actual_result = validate_required_fields(test_model_definition, required_fields_definition, test_active_context)

        assert_validator_result_success(actual_result)

    def test_validate_required_fields_with_missing_name_empty_fields(self):
        test_active_context = get_active_context(reload_context=True)

        test_definition = create_schema_definition("TestData")
        del test_definition.structure["schema"]["name"]

        required_fields_definition = test_active_context.get_definition_by_name(test_definition.get_root_key())
        actual_result = validate_required_fields(test_definition, required_fields_definition, test_active_context)

        assert_validator_result_failure(actual_result, "name", "field", "populated", "missing")
