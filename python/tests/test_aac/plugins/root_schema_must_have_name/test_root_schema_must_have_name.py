from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus
from aac.context.language_context import LanguageContext


from aac.plugins.root_schema_must_have_name.root_schema_must_have_name_impl import (
    plugin_name,
)


from aac.plugins.root_schema_must_have_name.root_schema_must_have_name_impl import (
    root_schema_has_name,
)


class TestRootSchemaMustHaveName(TestCase):

    def test_root_schema_has_name(self):
       context = LanguageContext()
       definitions = context.parse_and_load(root_schema_with_name)
       result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
       self.assertTrue(result.is_success())
       context.remove_definitions(definitions)

       definitions = context.parse_and_load(root_schema_without_name)
       result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
       self.assertFalse(result.is_success())
       context.remove_definitions(definitions)


root_schema_with_name = """
schema:
  name: test_schema
  root: test_root
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
"""

root_schema_without_name = """
schema:
  name: test_schema
  root: test_root
  fields:
    - name: test_field
      type: string
"""
