from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definition_by_name, get_definitions_by_root_key
from aac.plugins.validators import ValidatorPlugin, ValidatorResult
from aac.plugins.validators.exclusive_fields import _get_plugin_definitions, _get_plugin_validations, validate_exclusive_fields

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import create_schema_ext_definition, create_enum_ext_definition, create_field_entry


class TestExclusiveFieldsPlugin(ActiveContextTestCase):
    def test_module_register_validators(self):
        actual_validator_plugin = _get_plugin_validations()

        validation_definitions = get_definitions_by_root_key("validation", _get_plugin_definitions())
        self.assertEqual(1, len(validation_definitions))

        expected_validation_name = "Mutually exclusive fields"
        expected_validator_plugin = ValidatorPlugin(
            name=expected_validation_name, definition=validation_definitions[0], validation_function=(lambda x: x)
        )
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugin[0].name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugin[0].definition)

    def test_validate_exclusive_fields_no_defined_exclusive_fields(self):
        test_active_context = get_active_context()

        test_field_entry = create_field_entry("TestField", "string")
        test_definition = create_schema_ext_definition("TestSchemaExt", "schema", fields=[test_field_entry])
        del test_definition.structure["ext"]["schemaExt"]

        ext_schema = get_definition_by_name("extension", test_active_context.definitions)
        ext_schema_args = ext_schema.get_validations()[0].get("arguments")

        expected_result = ValidatorResult([], True)

        actual_result = validate_exclusive_fields(test_definition, ext_schema, test_active_context, *ext_schema_args)

        self.assertEqual(expected_result, actual_result)

    def test_validate_exclusive_fields_one_defined_exclusive_fields(self):
        test_active_context = get_active_context()

        test_field_entry = create_field_entry("TestField", "string")
        test_definition = create_schema_ext_definition("TestSchemaExt", "schema", fields=[test_field_entry])

        ext_schema = get_definition_by_name("extension", test_active_context.definitions)
        ext_schema_args = ext_schema.get_validations()[0].get("arguments")

        expected_result = ValidatorResult([], True)

        actual_result = validate_exclusive_fields(test_definition, ext_schema, test_active_context, *ext_schema_args)

        self.assertEqual(expected_result, actual_result)

    def test_validate_exclusive_fields_multiple_defined_exclusive_fields(self):
        test_active_context = get_active_context()

        test_field_entry = create_field_entry("TestField", "string")
        test_combined_ext_definition = create_schema_ext_definition("TestSchemaExt", "schema", fields=[test_field_entry])
        test_enum_definition = create_enum_ext_definition("TestEnumExt", "Primitives", values=["val1", "val2"])
        test_combined_ext_definition.structure["ext"]["enumExt"] = test_enum_definition.structure["ext"]["enumExt"]

        ext_schema = get_definition_by_name("extension", test_active_context.definitions)
        ext_schema_args = ext_schema.get_validations()[0].get("arguments")

        actual_result = validate_exclusive_fields(test_combined_ext_definition, ext_schema, test_active_context, *ext_schema_args)

        self.assertFalse(actual_result.is_valid)
