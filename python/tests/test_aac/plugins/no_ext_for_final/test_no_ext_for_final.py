from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus
from aac.context.language_context import LanguageContext


from aac.plugins.no_ext_for_final.no_ext_for_final_impl import plugin_name


from aac.plugins.no_ext_for_final.no_ext_for_final_impl import no_extension_for_final


class TestNoExtForFinal(TestCase):
    def test_no_extension_for_final(self):
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

        definitions = context.parse_and_load(root_schema_with_bad_ext)
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

root_schema_with_bad_ext = """
schema:
  name: TestSchema
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
    - name: TestSchema
      package: test_aac.plugins.no_ext_for_final
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
"""