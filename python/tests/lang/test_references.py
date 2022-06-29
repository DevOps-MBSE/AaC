from unittest import TestCase

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.references import get_definition_type_references_from_list, is_reference_format_valid, get_reference_target_definitions, _drill_into_nested_dict

from tests.helpers.parsed_definitions import create_schema_definition, create_schema_ext_definition, create_field_entry, create_model_definition


class TestLangReferences(TestCase):

    def test_get_definition_type_references_from_list(self):
        source_definition_name = "Source Def"
        source_definition = create_schema_definition(source_definition_name)

        reference_definition1_name = "Reference Def 1"
        reference_definition1_component1 = create_field_entry("Component1", source_definition_name)
        reference_definition1 = create_model_definition(reference_definition1_name, components=[reference_definition1_component1])

        reference_definition2_name = "Reference Def 2"
        reference_definition1_component1 = create_field_entry("New Field", "NewFieldType")
        reference_definition2 = create_schema_ext_definition(reference_definition2_name, source_definition_name)

        unrelated_definition = "Unrelated Def"
        unrelated_definition_field = create_field_entry("Other Field", "OtherFieldType")
        unrelated_definition = create_schema_definition(unrelated_definition, fields=[unrelated_definition_field])

        expected_references = [reference_definition1, reference_definition2]
        definitions_to_search = expected_references + [unrelated_definition, source_definition]

        actual_references = get_definition_type_references_from_list(source_definition, definitions_to_search)

        self.assertCountEqual(actual_references, expected_references)
        self.assertListEqual(expected_references, actual_references)

    def test_is_reference_format_valid(self):
        self.assertTrue(is_reference_format_valid("parent.child"))
        self.assertTrue(is_reference_format_valid("the_parent.child"))
        self.assertTrue(is_reference_format_valid("the-parent.child"))
        self.assertTrue(is_reference_format_valid("parent(name=\"MyModel\")"))
        self.assertTrue(is_reference_format_valid("parent(name=MyModel)"))
        self.assertTrue(is_reference_format_valid("parent.child(name=\"MyModel\")"))
        self.assertTrue(is_reference_format_valid("parent(name=\"MyModel\").child"))

        self.assertFalse(is_reference_format_valid("")[0])
        self.assertFalse(is_reference_format_valid("parent(name=value")[0])
        self.assertFalse(is_reference_format_valid("parent name=value)")[0])
        self.assertFalse(is_reference_format_valid("parent(name value)")[0])
        self.assertFalse(is_reference_format_valid("parent$.child")[0])
        self.assertFalse(is_reference_format_valid("parent.child#")[0])
        self.assertFalse(is_reference_format_valid("parent(name%=value)")[0])
        self.assertFalse(is_reference_format_valid("the parent.child")[0])
        self.assertFalse(is_reference_format_valid("parent.the child")[0])
        self.assertFalse(is_reference_format_valid("parent(the name=value")[0])
        self.assertFalse(is_reference_format_valid("parent(name=)")[0])

    def test_get_reference_target_definitions(self):

        language_context = get_active_context()

        # invalid reference should return empty list
        self.assertCountEqual(get_reference_target_definitions("", language_context), [])
        # get all models
        self.assertGreater(len(get_reference_target_definitions("model", language_context)), 0)
        # get schema with the name model
        self.assertEqual(len(get_reference_target_definitions("schema(name=model)", language_context)), 1)
        # get model with optional child field
        self.assertGreater(len(get_reference_target_definitions("model.behavior.input.python_type", language_context)), 0)
        # get model with inline selector
        self.assertEqual(len(get_reference_target_definitions("model.behavior(name=gen-plugin).input", language_context)), 1)
        # get model with multiple inline selectors
        self.assertEqual(len(get_reference_target_definitions("model(name=gen-plugin).behavior(type=command).input", language_context)), 1)

        # get non-existent root
        self.assertEqual(len(get_reference_target_definitions("not_a_valid_root", language_context)), 0)
        # get non-existent models
        self.assertEqual(len(get_reference_target_definitions("model(name=not_a_valid_name)", language_context)), 0)
        # get non-existent child
        self.assertEqual(len(get_reference_target_definitions("model.behavior(name=not_a_valid_name)", language_context)), 0)
        # get non-existent intermediate selector
        self.assertEqual(len(get_reference_target_definitions("model.behavior(name=not_a_valid_name).input", language_context)), 0)

    def test_drill_into_nested_fields(self):

        nested_dict = {"root": {"a": "a", "b": {"c": "c", "d": "d", "e": {"f": "f"}}}}
        search_keys = ["root", "b", "e"]
        expected_result = [{"f": "f"}]
        self.assertListEqual(_drill_into_nested_dict(search_keys, nested_dict), expected_result)

    def test_drill_into_nested_fields_no_root_found(self):

        nested_dict = {"root": {"a": "a", "b": {"c": "c", "d": "d", "e": {"f": "f"}}}}
        search_keys = ["nope", "b"]
        expected_result = []
        self.assertListEqual(_drill_into_nested_dict(search_keys, nested_dict), expected_result)

    def test_drill_into_nested_fields_no_nested_key_found(self):

        nested_dict = {"root": {"a": "a", "b": {"c": "c", "d": "d", "e": {"f": "f"}}}}
        search_keys = ["root", "z"]
        expected_result = []

        self.assertListEqual(_drill_into_nested_dict(search_keys, nested_dict), expected_result)

    def test_drill_into_nested_fields_nested_value_is_list(self):

        nested_dict = {"root": {"a": "a", "b": {"c": "c", "d": "d", "e": [{"f": "f"}, {"g": "g"}]}}}
        search_keys = ["root", "b", "e"]
        expected_result = [{"f": "f"}, {"g": "g"}]
        self.assertListEqual(_drill_into_nested_dict(search_keys, nested_dict), expected_result)

    def test_drill_into_nested_fields_intermediate_nested_value_is_list(self):

        nested_dict = {"root": [{"a": "a"}, {"b": {"c": "c", "d": "d", "e": {"f": "f"}}}]}
        search_keys = ["root", "b", "e"]
        expected_result = [{"f": "f"}]
        self.assertListEqual(_drill_into_nested_dict(search_keys, nested_dict), expected_result)
