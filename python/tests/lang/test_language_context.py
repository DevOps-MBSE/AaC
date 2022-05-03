from unittest import TestCase
from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
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

    def test_add_definitions_to_context_with_extensions(self):
        test_definition_field = create_field_entry("TestField", "string")
        test_definition_name = "myDef"
        test_definition = create_data_definition(test_definition_name, [test_definition_field])

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

        language_context = LanguageContext()
        self.assertEqual(0, len(language_context.definitions))

        language_context.add_definitions_to_context([test_definition, test_enum])
        self.assertEqual(2, len(language_context.definitions))

        self.assertIn(test_definition, language_context.definitions)
        self.assertIn(test_enum, language_context.definitions)

        self.assertEqual(1, len(test_definition.structure["data"]["fields"]))
        self.assertEqual(2, len(test_enum.structure["enum"]["values"]))

        language_context.add_definition_to_context(test_definition_ext)
        context_modified_test_definition = get_definition_by_name(test_definition_name, language_context.definitions)
        self.assertEqual(2, len(context_modified_test_definition.structure["data"]["fields"]))
        self.assertIn(data_ext_field_name, context_modified_test_definition.to_yaml())
        self.assertIn(data_ext_field_type, context_modified_test_definition.to_yaml())

        language_context.add_definition_to_context(test_enum_ext)
        context_modified_test_enum = get_definition_by_name(test_enum_name, language_context.definitions)
        self.assertEqual(3, len(context_modified_test_enum.structure["enum"]["values"]))
        self.assertIn(test_enum_ext_value, context_modified_test_enum.to_yaml())

    def test_remove_definitions_from_context(self):
        test_definition_field = create_field_entry("TestField", "string")
        test_definition_one = create_data_definition("Test1", [test_definition_field])
        test_definition_two = create_data_definition("Test2", [test_definition_field])

        language_context = get_initialized_language_context(core_spec_only=True)
        core_spec_definition_count = len(language_context.definitions)

        language_context.add_definitions_to_context([test_definition_one, test_definition_two])
        self.assertEqual(core_spec_definition_count + 2, len(language_context.definitions))

        language_context.remove_definitions_from_context([test_definition_one, test_definition_two])
        self.assertEqual(core_spec_definition_count, len(language_context.definitions))

    def test_update_definition_in_context(self):
        test_definition_field = create_field_entry("TestField", "string")
        test_definition_name = "myDef"
        test_definition = create_data_definition(test_definition_name, [test_definition_field])

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definition_to_context(test_definition)

        original_context_definition = language_context.get_definition_by_name(test_definition.name)
        self.assertEqual(test_definition.structure, original_context_definition.structure)

        test_definition.structure["data"]["fields"][0]["name"] = "NewTestField"
        language_context.update_definition_in_context(test_definition)

        altered_context_definition = language_context.get_definition_by_name(test_definition.name)
        self.assertEqual(test_definition.structure, altered_context_definition.structure)
        self.assertNotEqual(original_context_definition.structure, altered_context_definition.structure)

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
