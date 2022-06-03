from unittest import TestCase
from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.definitions.extensions import apply_extension_to_definition, remove_extension_from_definition

from tests.helpers.parsed_definitions import (
    REQUIRED_FIELDS_VALIDATION_STRING,
    create_schema_definition,
    create_schema_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
)


class TestDefinitionExtensions(TestCase):

    def test_apply_and_remove_extension_from_definition(self):
        test_definition_field = create_field_entry("TestField", "string")
        test_definition_name = "myDef"
        test_definition = create_schema_definition(test_definition_name, fields=[test_definition_field])

        data_ext_field_name = "extField"
        data_ext_field_type = "ExtField"
        ext_field = create_field_entry(data_ext_field_name, data_ext_field_type)
        test_definition_ext = create_schema_ext_definition("myDefExt", test_definition_name, fields=[ext_field], required=[data_ext_field_name])

        enum_val1 = "val1"
        enum_val2 = "val2"
        test_enum_name = "myEnum"
        test_enum = create_enum_definition(test_enum_name, values=[enum_val1, enum_val2])

        test_enum_ext_value = "extVal"
        test_enum_ext = create_enum_ext_definition("myEnumExt", test_enum_name, values=[test_enum_ext_value])

        language_context = get_initialized_language_context(core_spec_only=True)
        language_context.add_definitions_to_context([test_definition, test_enum])

        self.assertIn(test_definition, language_context.definitions)
        self.assertIn(test_enum, language_context.definitions)

        self.assertEqual(1, len(test_definition.structure["schema"]["fields"]))
        self.assertNotIn(REQUIRED_FIELDS_VALIDATION_STRING, test_definition.structure["schema"]["validation"])
        self.assertEqual(2, len(test_enum.structure["enum"]["values"]))

        apply_extension_to_definition(test_definition_ext, test_definition)
        apply_extension_to_definition(test_enum_ext, test_enum)

        # Assert Altered Extension State
        self.assertEqual(2, len(test_definition.structure["schema"]["fields"]))
        self.assertIn(REQUIRED_FIELDS_VALIDATION_STRING, test_definition.structure["schema"]["validation"])
        self.assertEqual(1, len(test_definition.structure["schema"]["validation"][REQUIRED_FIELDS_VALIDATION_STRING]["arguments"]))
        self.assertIn(data_ext_field_name, test_definition.to_yaml())
        self.assertIn(data_ext_field_type, test_definition.to_yaml())

        self.assertEqual(3, len(test_enum.structure["enum"]["values"]))
        self.assertIn(test_enum_ext_value, test_enum.to_yaml())

        remove_extension_from_definition(test_definition_ext, test_definition)
        remove_extension_from_definition(test_enum_ext, test_enum)

        # Assert Removed Extension State
        self.assertEqual(1, len(test_definition.structure["schema"]["fields"]))
        self.assertNotIn(REQUIRED_FIELDS_VALIDATION_STRING, test_definition.structure["schema"]["validation"])
        self.assertNotIn(data_ext_field_name, test_definition.to_yaml())
        self.assertNotIn(data_ext_field_type, test_definition.to_yaml())

        self.assertEqual(2, len(test_enum.structure["enum"]["values"]))
        self.assertNotIn(test_enum_ext_value, test_enum.to_yaml())
