from unittest import TestCase
from aac.lang.definition_helpers import get_definition_by_name

from aac.lang.language_context import LanguageContext
from aac.spec import get_aac_spec, get_primitives, get_root_keys

from tests.helpers.parsed_definitions import (
    create_data_definition,
    create_data_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
)


class TestDefinition(TestCase):

    def test_get_fields_with_empty_no_top_level_fields(self):
        test_definition = create_data_definition("EmptyData")
        test_definition.structure["data"] = {}

        actual_result = test_definition.get_fields()

        self.assertEqual({}, actual_result)

    def test_get_required_with_no_required_entries(self):
        test_definition = create_data_definition("EmptyData")

        actual_result = test_definition.get_required()

        self.assertEqual([], actual_result)

    def test_get_required_with_two_required_entries(self):
        test_required_sub_field_one = create_field_entry("ReqSubField1", "string")
        test_required_sub_field_two = create_field_entry("ReqSubField2", "string")
        test_fields = [test_required_sub_field_one, test_required_sub_field_two]
        test_required = [test_required_sub_field_one.get("name"), test_required_sub_field_two.get("name")]
        test_definition = create_data_definition("TestData", fields=test_fields, required=test_required)

        actual_result = test_definition.get_required()
        expected_result = [test_required_sub_field_one.get("name"), test_required_sub_field_two.get("name")]

        self.assertEqual(expected_result, actual_result)

    def test_is_enum_true(self):
        test_definition = create_enum_definition("Test", ["val1"])
        self.assertTrue(test_definition.is_enum())

    def test_is_enum_false(self):
        test_definition = create_data_definition("Test")
        self.assertFalse(test_definition.is_enum())

    def test_is_extension_true(self):
        test_definition = create_data_ext_definition("Test", "data")
        self.assertTrue(test_definition.is_extension())

    def test_is_extension_false(self):
        test_definition = create_data_definition("Test")
        self.assertFalse(test_definition.is_extension())

    def test_is_data_extension_true(self):
        test_definition = create_data_ext_definition("Test", "data")
        self.assertTrue(test_definition.is_data_extension())

    def test_is_data_extension_false(self):
        test_definition = create_enum_ext_definition("Test", "Primitives")
        self.assertFalse(test_definition.is_data_extension())

    def test_is_enum_extension_true(self):
        test_definition = create_enum_ext_definition("Test", "Primitives")
        self.assertTrue(test_definition.is_enum_extension())

    def test_is_enum_extension_false(self):
        test_definition = create_data_ext_definition("Test", "data")
        self.assertFalse(test_definition.is_enum_extension())
