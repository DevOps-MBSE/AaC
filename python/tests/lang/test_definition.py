from unittest import TestCase

from aac.plugins.validators.required_fields import get_required_fields, PLUGIN_NAME

from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_schema_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
    create_validation_entry,
)


class TestDefinition(TestCase):
    def test_uuid(self):
        self.assertTrue(create_schema_definition("Test").uid.is_safe)
        self.assertEqual(create_schema_definition("Test").uid, create_schema_definition("Test").uid)
        self.assertNotEqual(create_schema_definition("Test1").uid, create_schema_definition("Test2").uid)

    def test_get_fields_with_empty_no_top_level_fields(self):
        test_definition = create_schema_definition("EmptyData")
        test_definition.structure["schema"] = {}

        actual_result = test_definition.get_top_level_fields()

        self.assertEqual({}, actual_result)

    def test_get_required_with_no_required_entries(self):
        test_definition = create_schema_definition("EmptyData")

        actual_result = get_required_fields(test_definition)

        self.assertEqual([], actual_result)

    def test_get_required_with_two_required_entries(self):
        test_required_sub_field_one = create_field_entry("ReqSubField1", "string")
        test_required_sub_field_two = create_field_entry("ReqSubField2", "string")
        test_fields = [test_required_sub_field_one, test_required_sub_field_two]
        test_required = [test_required_sub_field_one.get("name"), test_required_sub_field_two.get("name")]
        required_fields_validator = create_validation_entry(PLUGIN_NAME, test_required)
        test_definition = create_schema_definition("TestData", fields=test_fields, validations=[required_fields_validator])

        actual_result = get_required_fields(test_definition)
        expected_result = [test_required_sub_field_one.get("name"), test_required_sub_field_two.get("name")]

        self.assertEqual(expected_result, actual_result)

    def test_is_enum_true(self):
        test_definition = create_enum_definition("Test", ["val1"])
        self.assertTrue(test_definition.is_enum())

    def test_is_enum_false(self):
        test_definition = create_schema_definition("Test")
        self.assertFalse(test_definition.is_enum())

    def test_is_extension_true(self):
        test_definition = create_schema_ext_definition("Test", "schema")
        self.assertTrue(test_definition.is_extension())

    def test_is_extension_false(self):
        test_definition = create_schema_definition("Test")
        self.assertFalse(test_definition.is_extension())

    def test_is_schema_extension_true(self):
        test_definition = create_schema_ext_definition("Test", "schema")
        self.assertTrue(test_definition.is_schema_extension())

    def test_is_schema_extension_false(self):
        test_definition = create_enum_ext_definition("Test", "Primitives")
        self.assertFalse(test_definition.is_schema_extension())

    def test_is_enum_extension_true(self):
        test_definition = create_enum_ext_definition("Test", "Primitives")
        self.assertTrue(test_definition.is_enum_extension())

    def test_is_enum_extension_false(self):
        test_definition = create_schema_ext_definition("Test", "schema")
        self.assertFalse(test_definition.is_enum_extension())
