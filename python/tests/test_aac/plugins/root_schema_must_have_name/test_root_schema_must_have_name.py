from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus
from aac.context.language_context import LanguageContext
from aac.context.language_error import LanguageError
from aac.in_out.parser._parser_error import ParserError
import traceback


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

    # def test_root_schema_has_name_fail(self):
    #     context = LanguageContext()
    #     definitions = context.parse_and_load(root_schema_without_name)
    #     result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #     self.assertFalse(result.is_success())
    #     context.remove_definitions(definitions)

    def test_root_schema_has_name_language_error1(self):
        context = LanguageContext()
        result = None
        try:
            definitions = context.parse_and_load(root_schema_without_name_language_error1)
            result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            self.assertFalse(result.is_success())
            context.remove_definitions(definitions)
            print("Completed try block")
        except ParserError as pe:
            print("ParserError1!")
            print(pe)
            self.assertFalse(True)
        except LanguageError as le:
            print("LanguageError1!")
            #print(le)
            # printing stack trace
            #traceback.print_exc() # File "/workspace/AaC/python/src/aac/context/definition_parser.py", line 601, in primitive_field_value_check
            self.assertFalse(False)
        except:
            print("Other unplanned error/exception1")
            self.assertFalse(True)

    def test_root_schema_has_name_language_error2(self):
        context = LanguageContext()
        result = None
        try:
            definitions = context.parse_and_load(root_schema_without_name_language_error2)
            result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            self.assertFalse(result.is_success())
            context.remove_definitions(definitions)
            print("Completed try block")
        except ParserError as pe:
            print("ParserError2!")
            print(pe)
            self.assertFalse(False)
        except LanguageError as le:
            print("LanguageError2!")
            # print(le)
            # printing stack trace
            # traceback.print_exc() # File "/workspace/AaC/python/src/aac/context/definition_parser.py", line 554, in field_instance_check
            self.assertFalse(False)
        except:
            print("Other unplanned error/exception2")
            self.assertFalse(True)

    def test_root_schema_has_name_parser_error3(self):
        context = LanguageContext()
        result = None
        try:
            definitions = context.parse_and_load(root_schema_without_name_parser_error3)
            result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            self.assertFalse(result.is_success())
            context.remove_definitions(definitions)
            print("Completed try block")
        except ParserError as pe:
            print("ParserError3!")
            # print(pe)
            # printing stack trace
            # traceback.print_exc() # File "/workspace/AaC/python/src/aac/in_out/parser/_yaml.py", line 103, in assert_definition_has_name
            self.assertFalse(False)
        except LanguageError as le:
            print("LanguageError3!")
            print(le)
            self.assertFalse(True)
        except:
            print("Other unplanned error/exception3")
            self.assertFalse(True)

    def test_root_schema_has_name_parser_error4(self):
        context = LanguageContext()
        result = None
        try:
            definitions = context.parse_and_load(root_schema_without_name_parser_error4)
            result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            self.assertFalse(result.is_success())
            context.remove_definitions(definitions)
            print("Completed try block")
        except ParserError as pe:
            print("ParserError4!")
            # print(pe)
             # printing stack trace
            # traceback.print_exc() # File "/workspace/AaC/python/src/aac/in_out/parser/_yaml.py", line 103, in assert_definition_has_name
            self.assertFalse(False)
        except LanguageError as le:
            print("LanguageError4!")
            print(le)
            self.assertFalse(True)
        except:
            print("Other unplanned error/exception4")
            self.assertFalse(True)

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

root_schema_without_name_language_error1 = """
schema:
  name: test_name
  root: test_root
  fields:
    - name:
      type: string
"""

root_schema_without_name_language_error2 = """
schema:
  name: test_name
  root: test_root
  fields:
      type: string
"""

root_schema_without_name_parser_error3 = """
schema:
  name:
  root: test_root
  fields:
    - name: name
      type: string
"""

root_schema_without_name_parser_error4 = """
schema:
  root: test_root
  fields:
    - name: name
      type: string
"""
