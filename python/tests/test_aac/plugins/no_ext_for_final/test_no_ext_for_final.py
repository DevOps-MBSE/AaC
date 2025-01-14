from unittest import TestCase
from aac.context.language_context import LanguageContext
from aac.plugins.no_ext_for_final.no_ext_for_final_impl import no_extension_for_final


class TestNoExtForFinal(TestCase):

    #  Nominal (expected pass) test with a single valid Schema definition
    def test_no_extension_for_final_nominal(self):
        context = LanguageContext()
        schema_definition = context.get_definitions_by_name("aac.lang.Schema")
        if len(schema_definition) != 1:
            self.fail("Expected to find one and only one Schema definition")
        schema_definition = schema_definition[0]

        definitions = context.parse_and_load(root_schema_with_good_ext)
        result = no_extension_for_final(definitions[0].instance, definitions[0], schema_definition.instance)
        self.assertTrue(result.is_success())
        result = no_extension_for_final(definitions[1].instance, definitions[1], schema_definition.instance)
        self.assertTrue(result.is_success())
        context.remove_definitions(definitions)

    #  Off-nominal (expected fail) tests
    def test_no_extension_for_final_offnominal(self):
        context = LanguageContext()
        schema_definition = context.get_definitions_by_name("aac.lang.Schema")
        if len(schema_definition) != 1:
            self.fail("Expected to find one and only one Schema definition")
        schema_definition = schema_definition[0]

        #  Off-nominal (expected fail) test with a circular schema definition
        #  TestSchema tries to extend TestSchema
        definitions = context.parse_and_load(root_schema_with_bad_ext_circular)
        result = no_extension_for_final(definitions[0].instance, definitions[0], schema_definition.instance)
        self.assertTrue(result.is_success())
        result = no_extension_for_final(definitions[1].instance, definitions[1], schema_definition.instance)
        self.assertFalse(result.is_success())
        self.assertEqual(result.messages[0].source, "No file to reference")
        context.remove_definitions(definitions)

        #  Off-nominal (expected fail) test with a invalid schema definition
        #  TestSchema defined twice
        definitions = context.parse_and_load(root_schema_with_bad_ext_duplicate)
        result = no_extension_for_final(definitions[0].instance, definitions[0], schema_definition.instance)
        self.assertTrue(result.is_success())
        result = no_extension_for_final(definitions[1].instance, definitions[1], schema_definition.instance)
        self.assertFalse(result.is_success())

        #  Off-nominal (expected fail) test with a invalid schema definition
        #  Specified parent to extend does not exist (TestDoesNotExist)
        definitions = context.parse_and_load(root_schema_with_bad_ext_does_not_exist)
        result = no_extension_for_final(definitions[0].instance, definitions[0], schema_definition.instance)
        self.assertTrue(result.is_success())
        result = no_extension_for_final(definitions[1].instance, definitions[1], schema_definition.instance)
        self.assertFalse(result.is_success())
        context.remove_definitions(definitions)


root_schema_with_good_ext = """
schema:
  name: TestParent
  package: test_aac.plugins.no_ext_for_final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
---
schema:
  name: TestChild
  package: test_aac.plugins.no_ext_for_final
  extends:
    - name: TestParent
      package: test_aac.plugins.no_ext_for_final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
"""

root_schema_with_bad_ext_circular = """
schema:
  name: TestParent
  package: test_aac.plugins.no_ext_for_final
  modifiers:
    - final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
---
schema:
  name: TestChild
  package: test_aac.plugins.no_ext_for_final
  extends:
    - name: TestParent
      package: test_aac.plugins.no_ext_for_final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
"""

root_schema_with_bad_ext_duplicate = """
schema:
  name: TestParent
  package: test_aac.plugins.no_ext_for_final
  modifiers:
    - final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
---
schema:
  name: TestParent
  package: test_aac.plugins.no_ext_for_final
  extends:
    - name: TestChild
      package: test_aac.plugins.no_ext_for_final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
"""

root_schema_with_bad_ext_does_not_exist = """
schema:
  name: TestParent
  package: test_aac.plugins.no_ext_for_final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
---
schema:
  name: TestChild
  package: test_aac.plugins.no_ext_for_final
  extends:
    - name: TestDoesNotExist
      package: test_aac.plugins.no_ext_for_final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
"""
