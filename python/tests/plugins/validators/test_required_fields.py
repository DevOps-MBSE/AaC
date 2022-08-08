from typing import Any

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definitions_by_root_key
from aac.plugins.validators import ValidatorPlugin
from aac.plugins.validators.required_fields import (
    _get_plugin_definitions,
    _get_plugin_validations,
    validate_required_fields,
    get_required_fields,
)
from aac.plugins.validators.required_fields._validate_required_fields import _is_field_populated

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_validator_result_failure, assert_validator_result_success
from tests.helpers.parsed_definitions import (
    create_behavior_entry,
    create_schema_definition,
    create_schema_ext_definition,
    create_field_entry,
    create_model_definition,
)


class TestRequiredFieldsPlugin(ActiveContextTestCase):
    def test_module_register_validators(self):
        actual_validator_plugins = _get_plugin_validations()

        validation_definitions = get_definitions_by_root_key("validation", _get_plugin_definitions())
        self.assertEqual(1, len(validation_definitions))

        expected_validator_plugin = ValidatorPlugin(
            name="Required fields are present", definition=validation_definitions[0], validation_function=(lambda x: x)
        )
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugins[0].name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugins[0].definition)

    def test_validate_required_fields_not_missing_required_fields_for_schema_definition(self):
        test_active_context = get_active_context()

        test_field_entry = create_field_entry("TestField", "string")
        test_definition = create_schema_definition("TestData", fields=[test_field_entry])

        required_fields_definition = test_active_context.get_definition_by_name(test_definition.get_root_key())
        actual_result = validate_required_fields(test_definition, required_fields_definition, test_active_context)

        assert_validator_result_success(actual_result)

    def test_validate_required_fields_no_missing_required_fields_for_model_definition(self):
        test_active_context = get_active_context()

        test_behavior_entry = create_behavior_entry("TestBehavior")
        test_model_definition = create_model_definition("TestModel", behavior=[test_behavior_entry])

        required_fields_definition = test_active_context.get_definition_by_name(test_model_definition.get_root_key())
        actual_result = validate_required_fields(test_model_definition, required_fields_definition, test_active_context)

        assert_validator_result_success(actual_result)

    def test_validate_required_fields_with_missing_name_empty_fields(self):
        test_active_context = get_active_context()

        test_definition = create_schema_definition("TestData")
        del test_definition.structure["schema"]["name"]

        required_fields_definition = test_active_context.get_definition_by_name(test_definition.get_root_key())
        required_fields = get_required_fields(required_fields_definition)
        actual_result = validate_required_fields(test_definition, required_fields_definition, test_active_context, *required_fields)

        assert_validator_result_failure(actual_result, "name", "field", "populated", "missing")

    def test_validate_required_fields_with_missing_name_empty_array_field(self):
        test_active_context = get_active_context()

        test_definition = create_schema_definition("TestData")

        required_fields_definition = test_active_context.get_definition_by_name(test_definition.get_root_key())
        required_fields = get_required_fields(required_fields_definition)
        actual_result = validate_required_fields(test_definition, required_fields_definition, test_active_context, *required_fields)

        assert_validator_result_failure(actual_result, "fields", "not populated")

    def test_required_fields_added_by_extension(self):
        test_active_context = get_active_context()

        schema_field_name = "TestField1"
        schema_field = create_field_entry(schema_field_name, "string")
        test_definition = create_schema_definition("TestSchema", fields=[schema_field])

        test_active_context.add_definition_to_context(test_definition)

        required_fields_definition = test_active_context.get_definition_by_name(test_definition.name)
        self.assertEqual(len(get_required_fields(required_fields_definition)), 0)

        schema_extension_field_name = "TestField2"
        schema_extension_field = create_field_entry(schema_extension_field_name, "string")
        test_extension = create_schema_ext_definition(f"{test_definition.name}Ext", test_definition.name, fields=[schema_extension_field], required=[schema_extension_field_name])

        test_active_context.add_definition_to_context(test_extension)

        required_fields_definition = test_active_context.get_definition_by_name(test_definition.name)
        required_fields = get_required_fields(required_fields_definition)

        self.assertEqual(len(required_fields), 1)
        self.assertEqual(required_fields[0], schema_extension_field_name)

    def test_is_field_populated(self):

        def param_test_is_field_populated(expected_value: bool, field_type: str, field_value: Any):
            actual_result = _is_field_populated(field_type, field_value)
            self.assertEqual((expected_value, field_type, field_value), (actual_result, field_type, field_value))

        params = [
            (True, "string", "Non-empty string"),
            (False, "string", ""),
            (False, "string", None),
            (True, "int", 1),
            (False, "int", None),
            (True, "bool", True),
            (True, "bool", False),
            (False, "bool", None),
        ]

        for param in params:
            param_test_is_field_populated(*param)
