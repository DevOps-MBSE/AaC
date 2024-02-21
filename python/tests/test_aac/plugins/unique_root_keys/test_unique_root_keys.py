from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus
from aac.context.language_context import LanguageContext


from aac.plugins.unique_root_keys.unique_root_keys_impl import plugin_name


from aac.plugins.unique_root_keys.unique_root_keys_impl import root_key_names_are_unique


class TestUniqueRootKeys(TestCase):
    def test_root_key_names_are_unique(self):
        context = LanguageContext()
        definitions = context.parse_and_load(GOOD_ROOTS)
        result = root_key_names_are_unique(context)
        self.assertTrue(result.is_success())
        context.remove_definitions(definitions)

        definitions = context.parse_and_load(BAD_ROOTS)
        result = root_key_names_are_unique(context)
        self.assertFalse(result.is_success())
        context.remove_definitions(definitions)



GOOD_ROOTS = """
schema:
  name: One
  package: test.root_keys
  root: one
  fields:
    - name: name
      type: string
---
schema:
  name: Two
  package: test.root_keys
  root: two
  fields:
    - name: name
      type: string
"""

BAD_ROOTS = """
schema:
  name: One
  package: test.root_keys
  root: one
  fields:
    - name: name
      type: string
---
schema:
  name: Two
  package: test.root_keys
  root: one
  fields:
    - name: name
      type: string
"""