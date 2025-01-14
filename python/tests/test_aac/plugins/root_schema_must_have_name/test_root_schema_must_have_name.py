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
    #     context = LanguageContext()
    #     definitions = context.parse_and_load(root_schema_with_name)
    #     result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #     self.assertTrue(result.is_success())
    #     context.remove_definitions(definitions)


    # #  This test starts with a normal properly formed schema
    # #  It then takes the result from parse_and_load and specifically removes the 'name'
    # #  It then calls root_schema_has_name which will not find the name it is looking for
    # def test_root_schema_has_name_fail(self):
    #     context = LanguageContext()
    #     try:
    #         # Obtain the definitions for a properly formed schema
    #         # This prevents any ParserErrors or LanguageErrors from being generated within parse_and_load
    #         definitions = context.parse_and_load(root_schema_with_name)

    #         # Now modify the fields to remove the 'name' field
    #         # Most of this 'try' is copied from root_schema_has_name::_get_fields
    #         try:
    #             schema = definitions[0].instance
    #             instance_fields = list[str]
    #             context: LanguageContext = LanguageContext()
    #             instance_fields: list[str] = []

    #             for field in schema.fields:
    #                 if field.name != 'name':
    #                     # Copy the field over except
    #                     # skip if it is 'name' to trigger the check in root_schema_has_name
    #                     instance_fields.append(field)

    #             if schema.extends:
    #                 for ext in schema.extends:
    #                     parent_schema = context.get_definitions_by_name(ext.name)
    #                     if len(parent_schema) == 1:
    #                         definitions[0].instance.fields.extend(_get_fields(parent_schema[0].instance))
    #             ## Set fields to the modified list without a 'name' field
    #             definitions[0].instance.fields = instance_fields
    #         except:
    #             traceback.print_exc()

    #         result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #         index = result.get_messages_as_string().find("must have a field named 'name'") # this is the message from line 61 of root_schema_has_name
    #         if index != -1:
    #             # Name message located
    #             self.assertFalse(result.is_success())
    #         else:
    #             # Name message missing
    #             self.assertFalse(True)
    #         context.remove_definitions(definitions)
    #     except AttributeError as ae:
    #         self.assertFalse(True)
    #     except ParserError as pe:
    #         self.assertFalse(True)
    #     except LanguageError as le:
    #         self.assertFalse(True)
    #     except:
    #         self.assertFalse(True)


    #  This test starts with a normal properly formed schema
    #  It then takes the result from parse_and_load and specifically creates a duplicate entry for the extended schema
    #  It then calls root_schema_has_name which will find a non-unique definition for an extended entry
    def test_root_schema_has_name_non_unique_definition(self):
        context = LanguageContext()
        try:
            # Obtain the definitions for a properly formed schema
            # This prevents any ParserErrors or LanguageErrors from being generated within parse_and_load
            definitions = context.parse_and_load(root_schema_with_extends)

            # Now modify the fields to remove the 'name' field
            try:
                schema = definitions[0].instance
                instance_fields = list[str]
                context: LanguageContext = LanguageContext()
                instance_fields: list[str] = []
                copy_field = None

                for field in schema.fields:
                    if field.name != 'extends':
                        print("NOT EXTENDS")
                        # Copy the field over except
                        # skip if it is 'name' to trigger the check in root_schema_has_name
                        instance_fields.append(field)
                        # Copy the field over
                    elif field.name == 'extends':
                        print("!!! EXTENDS !!!")
                        instance_fields.append(field)
                        copy_field = field
                        print(copy_field)

                print("A")
                if schema.extends:
                    print("B")
                    for ext in schema.extends:
                        print("C:")
                        parent_schema = context.get_definitions_by_name(ext.name)
                        parent_schema.append(context.get_definitions_by_name(ext.name))
                        print(len(parent_schema))
                        if len(parent_schema) > 0:
                            print("D")
                            inner_instance_fields = list[str]
                            inner_instance_fields: list[str] = []
                            print(len(inner_instance_fields))
                            inner_instance_fields.append(copy_field)
                            print(len(inner_instance_fields))
                            inner_instance_fields.append(copy_field)
                            print(len(inner_instance_fields))
                            instance_fields.extend(inner_instance_fields)
                            print("E")
                ## Set fields to the modified set without a 'name' field
                print("F")
                definitions[0].instance.fields = instance_fields

            except:
                traceback.print_exc()

            # Context/Parent schema
            # context.get_definitions_by_name(ext.name)
            print("HERE")
            #print(context.get_definitions_by_name("Schema")[0].instance)
            print(parent_schema)
            result = root_schema_has_name(definitions[0].instance, definitions[0], parent_schema)
            #result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
            self.assertFalse(result.is_success())
            context.remove_definitions(definitions)
        except AttributeError as ae:
            self.assertFalse(True)
        except ParserError as pe:
            self.assertFalse(True)
        except LanguageError as le:
            self.assertFalse(True)
        except:
            self.assertFalse(True)


    # #  This test should trigger a LanguageError exception from the parse_and_load call
    # #  So the only pass here is the self.assertFalse(False) in the LanguageError catch block
    # def test_root_schema_has_name_language_error1(self):

    #     context = LanguageContext()
    #     result = None
    #     try:
    #         definitions = context.parse_and_load(root_schema_without_name_language_error1)
    #         result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #         self.assertFalse(True)
    #         context.remove_definitions(definitions)
    #     except ParserError as pe:
    #         self.assertFalse(True)
    #     except LanguageError as le:
    #         self.assertFalse(False)
    #     except:
    #         self.assertFalse(True)


    # #  This test should trigger a LanguageError exception from the parse_and_load call
    # #  So the only pass here is the self.assertFalse(False) in the LanguageError catch block
    # def test_root_schema_has_name_language_error2(self):
    #     context = LanguageContext()
    #     result = None
    #     try:
    #         definitions = context.parse_and_load(root_schema_without_name_language_error2)
    #         result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #         self.assertFalse(True)
    #         context.remove_definitions(definitions)
    #     except ParserError as pe:
    #         self.assertFalse(True)
    #     except LanguageError as le:
    #         self.assertFalse(False)
    #     except:
    #         self.assertFalse(True)


    # #  This test should trigger a ParserError exception from the parse_and_load call
    # #  So the only pass here is the self.assertFalse(False) in the ParserError catch block
    # def test_root_schema_has_name_parser_error3(self):
    #     context = LanguageContext()
    #     result = None
    #     try:
    #         definitions = context.parse_and_load(root_schema_without_name_parser_error3)
    #         result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #         self.assertFalse(True)
    #         context.remove_definitions(definitions)
    #     except ParserError as pe:
    #         self.assertFalse(False)
    #     except LanguageError as le:
    #         self.assertFalse(True)
    #     except:
    #         self.assertFalse(True)


    # #  This test should trigger a ParserError exception from the parse_and_load call
    # #  So the only pass here is the self.assertFalse(False) in the ParserError catch block
    # def test_root_schema_has_name_parser_error4(self):
    #     context = LanguageContext()
    #     result = None
    #     try:
    #         definitions = context.parse_and_load(root_schema_without_name_parser_error4)
    #         result = root_schema_has_name(definitions[0].instance, definitions[0], context.get_definitions_by_name("Schema")[0].instance)
    #         self.assertFalse(True)
    #         context.remove_definitions(definitions)
    #     except ParserError as pe:
    #         self.assertFalse(False)
    #     except LanguageError as le:
    #         self.assertFalse(True)
    #     except:
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

root_schema_with_extends = """
schema:
  name: Schema
  extends:
    - package: aac.lang
      name: AacType
  package: aac.lang
  root: schema
  description: |
    A definition that defines the schema/structure of data.
  fields:
    - name: extends
      type: SchemaExtension[]
      description: |
        A list of Schema definition names that this definition inherits from.
    - name: test
      type: SchemaExtension[]
      description: |
        A list of Schema definition names that this definition inherits from.
    - name: modifiers
      type: dataref(modifier.name)[]
      description:
        A means of further defining the schema and how it can be used within the model.
    - name: root
      type: string
      description: |
        The root key to use when declaring an instance of the type in yaml/aac files.
    - name: fields
      type: Field[]
      description: |
        A list of fields that make up the definition.
      is_required: true
    - name: requirements
      type: dataref(req.id)[]
      description: |
        A list of requirements associated with this schema.
    - name: constraints
      type: SchemaConstraintAssignment[]
"""
