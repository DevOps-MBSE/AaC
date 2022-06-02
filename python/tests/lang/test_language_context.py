from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.language_context import LanguageContext
from aac.spec import get_aac_spec, get_primitives, get_root_keys

from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_schema_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
)


class TestLanguageContext(TestCase):

    ENUM_VALUE_EXAMPLE_ONE = "valueOne"
    ENUM_VALUE_EXAMPLE_TWO = "valueTwo"
    TEST_FIELD_DEFINITION_NAME = "TestField"
    TEST_SCHEMA_DEFINITION_NAME = "TestSchema"
    TEST_ENUM_DEFINITION_NAME = "TestEnum"
    TEST_SCHEMA_EXT_DEFINITION_NAME = "TestSchemaExtension"
    TEST_ENUM_EXT_DEFINITION_NAME = "TestEnumExtension"

    def test_add_definitions_to_context_with_extensions(self):
        test_definition_field = create_field_entry(self.TEST_FIELD_DEFINITION_NAME, "string")
        test_definition = create_schema_definition(self.TEST_SCHEMA_DEFINITION_NAME, fields=[test_definition_field])

        schema_ext_field_name = "extField"
        schema_ext_field_type = "ExtField"
        ext_field = create_field_entry(schema_ext_field_name, schema_ext_field_type)
        # Adding test_definition_field from the data definition above to simulate extending a definition with a duplicate value
        test_definition_ext = create_schema_ext_definition(self.TEST_SCHEMA_EXT_DEFINITION_NAME, self.TEST_SCHEMA_DEFINITION_NAME, fields=[ext_field, test_definition_field])

        test_enum = create_enum_definition(self.TEST_ENUM_DEFINITION_NAME, [self.ENUM_VALUE_EXAMPLE_ONE, self.ENUM_VALUE_EXAMPLE_TWO])

        test_enum_ext_value = "extVal"
        # Adding self.ENUM_VALUE_EXAMPLE_ONE from the enum above to simulate extending an enum with a duplicate value
        test_enum_ext = create_enum_ext_definition(self.TEST_ENUM_EXT_DEFINITION_NAME, self.TEST_ENUM_DEFINITION_NAME, values=[test_enum_ext_value, self.ENUM_VALUE_EXAMPLE_ONE])

        language_context = LanguageContext()
        self.assertEqual(0, len(language_context.definitions))

        language_context.add_definitions_to_context([test_definition, test_enum])
        self.assertEqual(2, len(language_context.definitions))

        self.assertIn(test_definition, language_context.definitions)
        self.assertIn(test_enum, language_context.definitions)

        # Assert pre-extension state
        self.assertEqual(1, len(test_definition.structure["schema"]["fields"]))
        self.assertEqual(2, len(test_enum.structure["enum"]["values"]))

        # Assert post-extension state
        language_context.add_definitions_to_context([test_definition_ext, test_enum_ext])
        context_modified_test_definition = language_context.get_definition_by_name(self.TEST_SCHEMA_DEFINITION_NAME)
        self.assertEqual(2, len(context_modified_test_definition.structure["schema"]["fields"]))
        self.assertIn(schema_ext_field_name, context_modified_test_definition.to_yaml())
        self.assertIn(schema_ext_field_type, context_modified_test_definition.to_yaml())

        context_modified_test_enum = language_context.get_definition_by_name(self.TEST_ENUM_DEFINITION_NAME)
        self.assertEqual(3, len(context_modified_test_enum.structure["enum"]["values"]))
        self.assertIn(test_enum_ext_value, context_modified_test_enum.to_yaml())

    def test_remove_definitions_from_context(self):
        test_definition_field = create_field_entry(self.TEST_FIELD_DEFINITION_NAME, "string")
        test_definition_one = create_schema_definition("Test1", fields=[test_definition_field])
        test_definition_two = create_schema_definition("Test2", fields=[test_definition_field])

        language_context = get_initialized_language_context(core_spec_only=True)
        core_spec_definition_count = len(language_context.definitions)

        language_context.add_definitions_to_context([test_definition_one, test_definition_two])
        self.assertEqual(core_spec_definition_count + 2, len(language_context.definitions))

        language_context.remove_definitions_from_context([test_definition_one, test_definition_two])
        self.assertEqual(core_spec_definition_count, len(language_context.definitions))

    def test_update_definition_in_context(self):
        test_definition_field = create_field_entry(self.TEST_FIELD_DEFINITION_NAME, "string")
        test_definition = create_schema_definition(self.TEST_SCHEMA_DEFINITION_NAME, fields=[test_definition_field])

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definition_to_context(test_definition)

        original_context_definition = language_context.get_definition_by_name(test_definition.name)
        self.assertEqual(test_definition.structure, original_context_definition.structure)

        test_definition.structure["schema"]["fields"][0]["name"] = "NewTestField"
        language_context.update_definition_in_context(test_definition)

        altered_context_definition = language_context.get_definition_by_name(test_definition.name)
        self.assertEqual(test_definition.structure, altered_context_definition.structure)
        self.assertNotEqual(original_context_definition.structure, altered_context_definition.structure)

    def test_remove_extension_definition_from_context(self):
        target_schema_definition_name = "model"
        target_enum_definition_name = "Primitives"
        schema_extension_field_name = self.TEST_FIELD_DEFINITION_NAME
        schema_extension_field = create_field_entry(schema_extension_field_name, "string")
        test_schema_extension = create_schema_ext_definition(self.TEST_SCHEMA_EXT_DEFINITION_NAME, target_schema_definition_name, fields=[schema_extension_field], required=[schema_extension_field_name])
        test_enum_extension = create_enum_ext_definition(self.TEST_ENUM_EXT_DEFINITION_NAME, target_enum_definition_name, values=[self.ENUM_VALUE_EXAMPLE_ONE, self.ENUM_VALUE_EXAMPLE_TWO])

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definitions_to_context([test_enum_extension, test_schema_extension])

        extended_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        extended_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        extended_enum_values = extended_enum_definition.get_top_level_fields().get("values")
        self.assertIn(self.ENUM_VALUE_EXAMPLE_ONE, extended_enum_values)
        self.assertIn(self.ENUM_VALUE_EXAMPLE_TWO, extended_enum_values)

        extended_schema_field_names = [field.get("name") for field in extended_schema_definition.get_top_level_fields().get("fields")]
        self.assertIn(schema_extension_field_name, extended_schema_field_names)
        self.assertIn(schema_extension_field_name, extended_schema_definition.get_required())

        language_context.remove_definitions_from_context([test_enum_extension, test_schema_extension])
        unextended_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        unextended_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        unextended_enum_values = unextended_enum_definition.get_top_level_fields().get("values")
        self.assertNotIn(self.ENUM_VALUE_EXAMPLE_ONE, unextended_enum_values)
        self.assertNotIn(self.ENUM_VALUE_EXAMPLE_TWO, unextended_enum_values)

        unextended_schema_field_names = [field.get("name") for field in unextended_schema_definition.get_top_level_fields().get("fields")]
        self.assertNotIn(schema_extension_field_name, unextended_schema_field_names)
        self.assertNotIn(schema_extension_field_name, extended_schema_definition.get_required())

    def test_update_extension_definition_in_context(self):
        target_schema_definition_name = "model"
        target_enum_definition_name = "Primitives"
        schema_extension_field_name = self.TEST_FIELD_DEFINITION_NAME
        schema_extension_field = create_field_entry(schema_extension_field_name, "string")
        test_schema_extension = create_schema_ext_definition(self.TEST_SCHEMA_EXT_DEFINITION_NAME, target_schema_definition_name, fields=[schema_extension_field], required=[schema_extension_field_name])
        test_enum_extension = create_enum_ext_definition(self.TEST_ENUM_EXT_DEFINITION_NAME, target_enum_definition_name, values=[self.ENUM_VALUE_EXAMPLE_ONE, self.ENUM_VALUE_EXAMPLE_TWO])

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definitions_to_context([test_enum_extension, test_schema_extension])

        extended_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        extended_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        extended_enum_values = extended_enum_definition.get_top_level_fields().get("values")
        self.assertIn(self.ENUM_VALUE_EXAMPLE_ONE, extended_enum_values)
        self.assertIn(self.ENUM_VALUE_EXAMPLE_TWO, extended_enum_values)

        extended_schema_field_names = [field.get("name") for field in extended_schema_definition.get_top_level_fields().get("fields")]
        self.assertIn(schema_extension_field_name, extended_schema_field_names)
        self.assertIn(schema_extension_field_name, extended_schema_definition.get_required())

        # Remove self.ENUM_VALUE_EXAMPLE_TWO from the enum extension
        test_enum_extension.structure["ext"]["enumExt"]["add"].remove(self.ENUM_VALUE_EXAMPLE_TWO)

        # Add an additional field
        additional_schema_extension_field_name = "Additionalfield"
        additional_schema_extension_field = create_field_entry(additional_schema_extension_field_name, "string")
        test_schema_extension.structure["ext"]["schemaExt"]["add"].append(additional_schema_extension_field)
        test_schema_extension.structure["ext"]["schemaExt"]["required"].append(additional_schema_extension_field_name)

        language_context.update_definitions_in_context([test_enum_extension, test_schema_extension])
        updated_schema_definition = language_context.get_definition_by_name(target_schema_definition_name)
        updated_enum_definition = language_context.get_definition_by_name(target_enum_definition_name)

        updated_enum_values = updated_enum_definition.get_top_level_fields().get("values")
        self.assertNotIn(self.ENUM_VALUE_EXAMPLE_TWO, updated_enum_values)

        updated_schema_field_names = [field.get("name") for field in updated_schema_definition.get_top_level_fields().get("fields")]
        self.assertIn(additional_schema_extension_field_name, updated_schema_field_names)
        self.assertIn(additional_schema_extension_field_name, updated_schema_definition.get_required())

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

        self.assertTrue(test_context.is_definition_type("schema"))
        self.assertFalse(test_context.is_definition_type("daaaaaaaaaata"))

    def test_get_root_keys(self):
        core_spec = get_aac_spec()
        test_context = LanguageContext(core_spec)

        expected_results = get_root_keys()
        actual_results = test_context.get_root_keys()

        self.assertEqual(expected_results, actual_results)
