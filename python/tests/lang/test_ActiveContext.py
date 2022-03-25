from unittest import TestCase

from aac.lang import ActiveContext

from tests.helpers.parsed_definitions import (
    create_data_definition,
    create_data_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
)


class TestActiveContext(TestCase):
    def test_add_definition_to_context_with_extensions(self):
        definition1_name = "myDef"
        definition1 = create_data_definition(definition1_name)

        data_ext_field_name = "extField"
        data_ext_field_type = "ExtField"
        ext_field = create_field_entry(data_ext_field_name, data_ext_field_type)
        definition1_ext = create_data_ext_definition("myDefExt", definition1_name, [ext_field])

        enum1_name = "myEnum"
        enum_val1 = "val1"
        enum_val2 = "val2"
        enum1 = create_enum_definition(enum1_name, [enum_val1, enum_val2])

        enum1_ext_value = "extVal"
        enum1_ext = create_enum_ext_definition("myEnumExt", enum1_name, [enum1_ext_value])

        active_context = ActiveContext()
        self.assertEqual(0, len(active_context.context_definitions))

        active_context.add_definition_to_context(definition1)
        self.assertEqual(1, len(active_context.context_definitions))

        active_context.add_definition_to_context(enum1)
        self.assertEqual(2, len(active_context.context_definitions))

        self.assertIn(definition1, active_context.context_definitions)
        self.assertIn(enum1, active_context.context_definitions)

        self.assertEqual(0, len(definition1.definition["data"]["fields"]))
        self.assertEqual(2, len(enum1.definition["enum"]["values"]))

        active_context.add_definition_to_context(definition1_ext)
        self.assertEqual(1, len(definition1.definition["data"]["fields"]))
        self.assertIn(data_ext_field_name, definition1.to_yaml())
        self.assertIn(data_ext_field_type, definition1.to_yaml())

        active_context.add_definition_to_context(enum1_ext)
        self.assertEqual(3, len(enum1.definition["enum"]["values"]))
        self.assertIn(enum1_ext_value, enum1.to_yaml())
