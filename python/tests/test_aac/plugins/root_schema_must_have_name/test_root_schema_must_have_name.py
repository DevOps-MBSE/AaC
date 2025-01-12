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

    # def test_root_schema_has_name(self):
    #     print("")
    #     context = LanguageContext()
    #     definitions = context.parse_and_load(root_schema_with_name)
    #     result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #     self.assertTrue(result.is_success())
    #     context.remove_definitions(definitions)

    # def _get_test_fields(schema) -> list[str]:
    #     """Returns a list of the fields in the parent schema."""
    #     print("IN _get_test_fields IN")
    #     context: LanguageContext = LanguageContext()
    #     fields: list[str] = []
    #     for field in schema.fields:
    #         if field.name != 'name':
    #             fields.append(field.name)
    #         else:
    #             print("Excluding name")
    #     if schema.extends:
    #         for ext in schema.extends:
    #             parent_schema = context.get_definitions_by_name(ext.name)
    #             if len(parent_schema) == 1:
    #                 fields.extend(_get_fields(parent_schema[0].instance))
    #     return fields

    def test_root_schema_has_name_fail(self):
        print("\n\n***\n")
        context = LanguageContext()
        try:
            # Obtain the definitions for a properly formed schema
            # This prevents any ParserErrors or LanguageErrors from being generated within parse_and_load
            definitions = context.parse_and_load(root_schema_with_name)

            # Now modify the fields to remove the 'name' field
            try:
                schema = definitions[0].instance
                instance_fields = list[str]
                context: LanguageContext = LanguageContext()
                instance_fields: list[str] = []
                for field in schema.fields:
                    if field.name != 'name':
                        instance_fields.append(field)
                    # else:
                        # Excluding name
                if schema.extends:
                    for ext in schema.extends:
                        parent_schema = context.get_definitions_by_name(ext.name)
                        if len(parent_schema) == 1:
                            fields.extend(_get_fields(parent_schema[0].instance))
                ## Set fields to the modified set without a 'name' field
                definitions[0].instance.fields = instance_fields
            except:
                traceback.print_exc()

            result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            index = result.get_messages_as_string().find("must have a field named 'name")
            if index != -1:
                # Name message located
                self.assertFalse(result.is_success())
            else:
                # Name message missing
                self.assertFalse(True)
            context.remove_definitions(definitions)
        except AttributeError as ae:
            self.assertFalse(True)
        except ParserError as pe:
            self.assertFalse(True)
        except LanguageError as le:
            self.assertFalse(True)
        except:
            self.assertFalse(True)

    # def test_root_schema_has_name_language_error1(self):

    #     context = LanguageContext()
    #     result = None
    #     try:
    #         definitions = context.parse_and_load(root_schema_without_name_language_error1)
    #         result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #         self.assertFalse(result.is_success())
    #         context.remove_definitions(definitions)
    #         print("Completed try block")
    #     except ParserError as pe:
    #         print("ParserError1!")
    #         print(pe)
    #         self.assertFalse(True)
    #     except LanguageError as le:
    #         print("LanguageError1!")
    #         #print(le)
    #         # #printing stack trace
    #         #traceback.print_exc() # File "/workspace/AaC/python/src/aac/context/definition_parser.py", line 601, in primitive_field_value_check
    #         self.assertFalse(False)
    #     except:
    #         print("Other unplanned error/exception1")
    #         traceback.print_exc()
    #         self.assertFalse(True)

    # def test_root_schema_has_name_language_error2(self):
    #     context = LanguageContext()
    #     result = None
    #     try:
    #         definitions = context.parse_and_load(root_schema_without_name_language_error2)
    #         result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #         self.assertFalse(result.is_success())
    #         context.remove_definitions(definitions)
    #         print("Completed try block")
    #     except ParserError as pe:
    #         print("ParserError2!")
    #         print(pe)
    #         self.assertFalse(True)
    #     except LanguageError as le:
    #         print("LanguageError2!")
    #         # print(le)
    #         # #printing stack trace
    #         # traceback.print_exc() # File "/workspace/AaC/python/src/aac/context/definition_parser.py", line 554, in field_instance_check
    #         self.assertFalse(False)
    #     except:
    #         print("Other unplanned error/exception2")
    #         self.assertFalse(True)

    # def test_root_schema_has_name_parser_error3(self):
    #     context = LanguageContext()
    #     result = None
    #     try:
    #         definitions = context.parse_and_load(root_schema_without_name_parser_error3)
    #         result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #         self.assertFalse(result.is_success())
    #         context.remove_definitions(definitions)
    #         print("Completed try block")
    #     except ParserError as pe:
    #         print("ParserError3!")
    #         # print(pe)
    #         # printing stack trace
    #         # traceback.print_exc() # File "/workspace/AaC/python/src/aac/in_out/parser/_yaml.py", line 103, in assert_definition_has_name
    #         self.assertFalse(False)
    #     except LanguageError as le:
    #         print("LanguageError3!")
    #         print(le)
    #         self.assertFalse(True)
    #     except:
    #         print("Other unplanned error/exception3")
    #         self.assertFalse(True)

    # def test_root_schema_has_name_parser_error4(self):
    #     context = LanguageContext()
    #     result = None
    #     try:
    #         definitions = context.parse_and_load(root_schema_without_name_parser_error4)
    #         result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #         self.assertFalse(result.is_success())
    #         context.remove_definitions(definitions)
    #         print("Completed try block")
    #     except ParserError as pe:
    #         print("ParserError4!")
    #         # print(pe)
    #         # printing stack trace
    #         # traceback.print_exc() # File "/workspace/AaC/python/src/aac/in_out/parser/_yaml.py", line 103, in assert_definition_has_name
    #         self.assertFalse(False)
    #     except LanguageError as le:
    #         print("LanguageError4!")
    #         print(le)
    #         self.assertFalse(True)
    #     except:
    #         print("Other unplanned error/exception4")
    #         self.assertFalse(True)

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
