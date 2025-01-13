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


    #  This test starts with a normal properly formed schema
    #  It then takes the result from parse_and_load and specifically removes the 'name'
    #  It then calls root_schema_has_name which will not find the name it is looking for
    def test_root_schema_has_name_fail(self):
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
                        # Copy the field over if the name is 'name'
                        # skip if it is 'name' to trigger the check in root_schema_has_name
                        instance_fields.append(field)

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
            index = result.get_messages_as_string().find("must have a field named 'name'") # this is the message from line 61 of root_schema_has_name
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


    #  This test should trigger a LanguageError exception from the parse_and_load call
    #  So the only pass here is the self.assertFalse(False) in the LanguageError catch block
    def test_root_schema_has_name_language_error1(self):

        context = LanguageContext()
        result = None
        try:
            definitions = context.parse_and_load(root_schema_without_name_language_error1)
            result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            self.assertFalse(True)
            context.remove_definitions(definitions)
        except ParserError as pe:
            self.assertFalse(True)
        except LanguageError as le:
            self.assertFalse(False)
        except:
            self.assertFalse(True)


    #  This test should trigger a LanguageError exception from the parse_and_load call
    #  So the only pass here is the self.assertFalse(False) in the LanguageError catch block
    def test_root_schema_has_name_language_error2(self):
        context = LanguageContext()
        result = None
        try:
            definitions = context.parse_and_load(root_schema_without_name_language_error2)
            result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            self.assertFalse(True)
            context.remove_definitions(definitions)
        except ParserError as pe:
            self.assertFalse(True)
        except LanguageError as le:
            self.assertFalse(False)
        except:
            self.assertFalse(True)


    #  This test should trigger a ParserError exception from the parse_and_load call
    #  So the only pass here is the self.assertFalse(False) in the ParserError catch block
    def test_root_schema_has_name_parser_error3(self):
        context = LanguageContext()
        result = None
        try:
            definitions = context.parse_and_load(root_schema_without_name_parser_error3)
            result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            self.assertFalse(True)
            context.remove_definitions(definitions)
        except ParserError as pe:
            self.assertFalse(False)
        except LanguageError as le:
            self.assertFalse(True)
        except:
            self.assertFalse(True)


    #  This test should trigger a ParserError exception from the parse_and_load call
    #  So the only pass here is the self.assertFalse(False) in the ParserError catch block
    def test_root_schema_has_name_parser_error4(self):
        context = LanguageContext()
        result = None
        try:
            definitions = context.parse_and_load(root_schema_without_name_parser_error4)
            result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            self.assertFalse(True)
            context.remove_definitions(definitions)
        except ParserError as pe:
            self.assertFalse(False)
        except LanguageError as le:
            self.assertFalse(True)
        except:
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
