from aac.io.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.collections import get_definition_by_name, get_definitions_by_root_key
from aac.lang.definitions.source_location import SourceLocation
from aac.plugins.contributions.contribution_types import DefinitionValidationContribution
from aac.plugins.validators import ValidatorResult
from aac.plugins.validators.exclusive_fields import (
    _get_plugin_definitions,
    _get_plugin_validations,
    validate_exclusive_fields,
)

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_definitions_equal
from tests.helpers.parsed_definitions import (
    create_enum_ext_definition,
    create_field_entry,
    create_schema_ext_definition,
)


class TestExclusiveFieldsPlugin(ActiveContextTestCase):
    def test_module_register_validators(self):
        actual_validator_plugins = _get_plugin_validations()

        validation_definitions = get_definitions_by_root_key("validation", _get_plugin_definitions())
        self.assertEqual(1, len(validation_definitions))

        validation_definition = validation_definitions[0]
        expected_definition_validation = DefinitionValidationContribution(
            name=validation_definition.name,
            definition=validation_definition,
            validation_function=(lambda x: x),
        )
        self.assertEqual(expected_definition_validation.name, actual_validator_plugins[0].name)
        assert_definitions_equal(expected_definition_validation.definition, actual_validator_plugins[0].definition)

    def test_validate_exclusive_fields_no_defined_exclusive_fields(self):
        test_active_context = get_active_context()

        test_field_entry = create_field_entry("TestField", "string")
        test_definition = create_schema_ext_definition("TestSchemaExt", "schema", fields=[test_field_entry])
        del test_definition.structure["ext"]["schemaExt"]

        ext_schema = get_definition_by_name("extension", test_active_context.definitions)
        ext_schema_args = ext_schema.get_validations()[0].get("arguments")

        expected_result = ValidatorResult([test_definition])

        actual_result = validate_exclusive_fields(test_definition, ext_schema, test_active_context, *ext_schema_args)

        self.assertEqual(expected_result, actual_result)

    def test_validate_exclusive_fields_one_defined_exclusive_fields(self):
        test_active_context = get_active_context()

        test_field_entry = create_field_entry("TestField", "string")
        test_definition = create_schema_ext_definition("TestSchemaExt", "schema", fields=[test_field_entry])

        ext_schema = get_definition_by_name("extension", test_active_context.definitions)
        ext_schema_args = ext_schema.get_validations()[0].get("arguments")

        expected_result = ValidatorResult([test_definition])

        actual_result = validate_exclusive_fields(test_definition, ext_schema, test_active_context, *ext_schema_args)

        self.assertEqual(expected_result, actual_result)

    def test_validate_exclusive_fields_multiple_defined_exclusive_fields(self):
        test_active_context = get_active_context()

        test_field_entry = create_field_entry("TestField", "string")
        test_combined_ext_definition = create_schema_ext_definition("TestSchemaExt", "schema", fields=[test_field_entry])
        test_enum_definition = create_enum_ext_definition("TestEnumExt", "Primitives", values=["val1", "val2"])
        test_combined_ext_definition.structure["ext"]["enumExt"] = test_enum_definition.structure["ext"]["enumExt"]
        test_combined_ext_definition, *_ = parse(test_combined_ext_definition.to_yaml())

        ext_schema = get_definition_by_name("extension", test_active_context.definitions)
        ext_schema_args = ext_schema.get_validations()[0].get("arguments")

        expected_finding_location = SourceLocation(10, 2, 164, 7)

        actual_result = validate_exclusive_fields(
            test_combined_ext_definition, ext_schema, test_active_context, *ext_schema_args
        )

        self.assertFalse(actual_result.is_valid())
        self.assertEqual(
            actual_result.findings.get_error_findings()[0].location.location,
            expected_finding_location,
        )
