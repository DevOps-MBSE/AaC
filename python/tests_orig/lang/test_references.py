from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import DEFINITION_NAME_MODEL
from aac.lang.definitions.references import (
    get_definition_type_references_from_list,
    is_reference_format_valid,
    get_reference_target_definitions,
    _drill_into_nested_dict,
)
from aac.io.parser import parse

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.parsed_definitions import (
    create_schema_definition,
    create_schema_ext_definition,
    create_field_entry,
    create_model_definition,
)


class TestLangReferences(ActiveContextTestCase):
    def test_get_definition_type_references_from_list(self):
        source_definition_name = "Source Def"
        source_definition = create_schema_definition(source_definition_name)

        reference_definition1_name = "Reference Def 1"
        reference_definition1_component1 = create_field_entry("Component1", source_definition_name)
        reference_definition1 = create_model_definition(
            reference_definition1_name, components=[reference_definition1_component1]
        )

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
        self.assertTrue(is_reference_format_valid('parent(name="MyModel")'))
        self.assertTrue(is_reference_format_valid("parent(name=MyModel)"))
        self.assertTrue(is_reference_format_valid('parent.child(name="MyModel")'))
        self.assertTrue(is_reference_format_valid('parent(name="MyModel").child'))

        self.assertFalse(is_reference_format_valid(""))
        self.assertFalse(is_reference_format_valid("parent(name=value"))
        self.assertFalse(is_reference_format_valid("parent name=value)"))
        self.assertFalse(is_reference_format_valid("parent(name value)"))
        self.assertFalse(is_reference_format_valid("parent$.child"))
        self.assertFalse(is_reference_format_valid("parent.child#"))
        self.assertFalse(is_reference_format_valid("parent(name%=value)"))
        self.assertFalse(is_reference_format_valid("the parent.child"))
        self.assertFalse(is_reference_format_valid("parent.the child"))
        self.assertFalse(is_reference_format_valid("parent(the name=value"))
        self.assertFalse(is_reference_format_valid("parent(name=)"))

    def test_get_reference_target_definitions(self):
        language_context = get_active_context(reload_context=True)

        # invalid reference should return empty list
        self.assertCountEqual(get_reference_target_definitions("", language_context), [])
        # get all models
        self.assertGreater(len(get_reference_target_definitions("plugin", language_context)), 0)
        # get schema with the name model
        self.assertEqual(len(get_reference_target_definitions(f"schema(name={DEFINITION_NAME_MODEL})", language_context)), 1)
        # get model with optional child field
        self.assertGreater(len(get_reference_target_definitions("plugin.commands.input.python_type", language_context)), 0)
        # get model with inline selector
        self.assertEqual(len(get_reference_target_definitions("plugin.commands(name=gen-plugin).input", language_context)), 1)
        # get model with multiple inline selectors
        self.assertEqual(
            len(
                get_reference_target_definitions(
                    'plugin(name="Generate Plugin").commands(group=Generation).input', language_context
                )
            ),
            1,
        )

        # get non-existent root
        self.assertEqual(len(get_reference_target_definitions("not_a_valid_root", language_context)), 0)
        # get non-existent models
        self.assertEqual(len(get_reference_target_definitions("model(name=not_a_valid_name)", language_context)), 0)
        # get non-existent child
        self.assertEqual(len(get_reference_target_definitions("model.behavior(name=not_a_valid_name)", language_context)), 0)
        # get non-existent intermediate selector
        self.assertEqual(
            len(get_reference_target_definitions("model.behavior(name=not_a_valid_name).input", language_context)), 0
        )

    def test_get_reference_target_definitions_with_non_string_selector_value(self):
        # get model using selector that targets a non-string value
        language_context = get_active_context()
        definitions = parse(TEST_MODEL_WITH_NON_STRING_VALUE)
        language_context.add_definitions_to_context(definitions)
        self.assertEqual(len(get_reference_target_definitions("deployment.assemblies(quantity=1)", language_context)), 1)

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


TEST_MODEL_WITH_NON_STRING_VALUE = """
schema:
  name: Deployment
  root: deployment
  fields:
    - name: my_name
      type: string
      description: |
        Some random string.
---
schema:
  name: Assembly
  root: assembly
  fields:
    - name: my_other_name
      type: string
      description: |
        Some random string.
---
deployment:
  name: My_New_Apartment
  description: The place I'm going to live.
  location: Crystal Terrace Apartments Unit 1234
  sub-deployments:
    - deployment-ref: deployment.assemblies(quantity=1)
      quantity: 1
---
deployment:
  name: Living_Room
  description:  The place I'll hang out a lot.
  location: The large room off the entry way
  assemblies:
    - assembly-ref: assembly(name="Entertainment_System")
      quantity: 1
---
assembly:
  name: Entertainment_System
  description:  Mostly electronic toys
"""
