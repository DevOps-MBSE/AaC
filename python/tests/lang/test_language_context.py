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


class TestLanguageContext(TestCase):

    def test_add_definition_to_context_with_extensions(self):
        test_definition_name = "myDef"
        test_definition = create_data_definition(test_definition_name)

        data_ext_field_name = "extField"
        data_ext_field_type = "ExtField"
        ext_field = create_field_entry(data_ext_field_name, data_ext_field_type)
        test_definition_ext = create_data_ext_definition("myDefExt", test_definition_name, [ext_field])

        enum_val1 = "val1"
        enum_val2 = "val2"
        test_enum_name = "myEnum"
        test_enum = create_enum_definition(test_enum_name, [enum_val1, enum_val2])

        test_enum_ext_value = "extVal"
        test_enum_ext = create_enum_ext_definition("myEnumExt", test_enum_name, [test_enum_ext_value])

        active_context = LanguageContext()
        self.assertEqual(0, len(active_context.definitions))

        active_context.add_definition_to_context(test_definition)
        self.assertEqual(1, len(active_context.definitions))

        active_context.add_definition_to_context(test_enum)
        self.assertEqual(2, len(active_context.definitions))

        self.assertIn(test_definition, active_context.definitions)
        self.assertIn(test_enum, active_context.definitions)

        self.assertEqual(0, len(test_definition.structure["data"]["fields"]))
        self.assertEqual(2, len(test_enum.structure["enum"]["values"]))

        active_context.add_definition_to_context(test_definition_ext)
        context_modified_test_definition = get_definition_by_name(test_definition_name, active_context.definitions)
        self.assertEqual(1, len(context_modified_test_definition.structure["data"]["fields"]))
        self.assertIn(data_ext_field_name, context_modified_test_definition.to_yaml())
        self.assertIn(data_ext_field_type, context_modified_test_definition.to_yaml())

        active_context.add_definition_to_context(test_enum_ext)
        context_modified_test_enum = get_definition_by_name(test_enum_name, active_context.definitions)
        self.assertEqual(3, len(context_modified_test_enum.structure["enum"]["values"]))
        self.assertIn(test_enum_ext_value, context_modified_test_enum.to_yaml())

    def test_get_primitives_with_unextended_context(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        expected_results = get_primitives()
        actual_results = test_context.get_primitive_types()

        self.assertEqual(expected_results, actual_results)

    def test_get_get_defined_types_with_unextended_context(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        actual_results = test_context.get_defined_types()
        expected_results = [definition.name for definition in test_context.definitions]

        self.assertListEqual(expected_results, actual_results)

    def test_is_primitive(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        self.assertTrue(test_context.is_primitive_type("string"))
        self.assertFalse(test_context.is_primitive_type("striiiiiiiiiiiiiiing"))

    def test_is_defined_type(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        self.assertTrue(test_context.is_definition_type("data"))
        self.assertFalse(test_context.is_definition_type("daaaaaaaaaata"))

    def test_get_root_keys(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        expected_results = get_root_keys()
        actual_results = test_context.get_root_keys()

        self.assertEqual(expected_results, actual_results)
