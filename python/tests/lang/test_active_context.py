from unittest import TestCase
from aac.lang.definition_helpers import get_definition_by_name

from aac.lang import ActiveContext
from aac.spec import get_aac_spec, get_primitives, get_root_keys

from tests.helpers.parsed_definitions import (
    create_data_definition,
    create_data_ext_definition,
    create_enum_definition,
    create_enum_ext_definition,
    create_field_entry,
)


class TestActiveContext(TestCase):

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

        active_context = ActiveContext()
        self.assertEqual(0, len(active_context.context_definitions))

        active_context.add_definition_to_context(test_definition)
        self.assertEqual(1, len(active_context.context_definitions))

        active_context.add_definition_to_context(test_enum)
        self.assertEqual(2, len(active_context.context_definitions))

        self.assertIn(test_definition, active_context.context_definitions)
        self.assertIn(test_enum, active_context.context_definitions)

        self.assertEqual(0, len(test_definition.definition["data"]["fields"]))
        self.assertEqual(2, len(test_enum.definition["enum"]["values"]))

        active_context.add_definition_to_context(test_definition_ext)
        context_modified_test_definition = get_definition_by_name(active_context.context_definitions, test_definition_name)
        self.assertEqual(1, len(context_modified_test_definition.definition["data"]["fields"]))
        self.assertIn(data_ext_field_name, context_modified_test_definition.to_yaml())
        self.assertIn(data_ext_field_type, context_modified_test_definition.to_yaml())

        active_context.add_definition_to_context(test_enum_ext)
        context_modified_test_enum = get_definition_by_name(active_context.context_definitions, test_enum_name)
        self.assertEqual(3, len(context_modified_test_enum.definition["enum"]["values"]))
        self.assertIn(test_enum_ext_value, context_modified_test_enum.to_yaml())

    def test_get_primitives_with_unextended_context(self):
        core_spec = get_aac_spec()
        test_context = ActiveContext(core_spec)

        expected_results = get_primitives()
        actual_results = test_context.get_primitives()

        self.assertEqual(expected_results, actual_results)

    def test_get_root_keys(self):
        core_spec = get_aac_spec()
        test_context = ActiveContext(core_spec)

        expected_results = get_root_keys()
        actual_results = test_context.get_root_keys()

        self.assertEqual(expected_results, actual_results)
