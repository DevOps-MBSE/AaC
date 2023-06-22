from os.path import basename, sep
from tempfile import TemporaryDirectory
from typing import Optional
from unittest import TestCase

from aac.io.constants import AAC_DOCUMENT_EXTENSION, YAML_DOCUMENT_SEPARATOR
from aac.io.parser import parse, ParserError
from aac.lang.constants import (
    BEHAVIOR_TYPE_REQUEST_RESPONSE,
    DEFINITION_FIELD_NAME,
    ROOT_KEY_ENUM,
    ROOT_KEY_IMPORT,
    ROOT_KEY_MODEL,
    ROOT_KEY_SCHEMA,
)
from aac.lang.definitions import collections
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.source_location import SourceLocation

from tests.helpers.io import TemporaryTestFile
from tests.helpers.parsed_definitions import create_enum_definition, create_import_definition


PARSER_TEST_SOURCE = "<parser test>"


class TestParser(TestCase):
    def get_lexeme_values_for_definition(self, name: str, definitions: list[Definition]) -> list[str]:
        lexemes = [definition.lexemes for definition in definitions if definition.name == name][0]
        return [lexeme.value for lexeme in lexemes]

    def check_definition(self, definition: Optional[Definition], name: str, type: str):
        self.assertIsNotNone(definition)
        self.assertEqual(type, definition.get_root_key())
        self.assertEqual(name, definition.name)

    def check_parser_errors(self, filespec: str, *error_messages: list[str]):
        with self.assertRaises(ParserError) as cm:
            parse(filespec)

        # Assert that each error message is contained in the returned error message string.
        errors = "\n".join(cm.exception.errors)
        list(map(lambda e: self.assertIn(e, errors), error_messages))
        self.assertEqual(cm.exception.source, filespec)

    def test_can_get_lexemes_from_parsed_architecture_file(self):
        with TemporaryTestFile(TEST_MESSAGE_CONTENTS.strip()) as test_yaml:
            parsed_definitions = parse(test_yaml.name)
            self.assertEqual(1, len(parsed_definitions))
            parsed_definition = parsed_definitions[0]

            self.assertGreaterEqual(len(parsed_definition.lexemes), 2)

            first, second, *_ = parsed_definition.lexemes
            self.assertEqual(first.source, test_yaml.name)
            self.assertEqual(first.value, ROOT_KEY_SCHEMA)
            self.assertEqual(first.location, SourceLocation(0, 0, 0, 6))

            self.assertEqual(second.source, test_yaml.name)
            self.assertEqual(second.value, DEFINITION_FIELD_NAME)
            self.assertEqual(second.location, SourceLocation(1, 2, 10, 4))

    def test_can_handle_architecture_file_with_imports(self):
        with (
            TemporaryDirectory() as temp_dir,
            TemporaryTestFile(TEST_MESSAGE_CONTENTS, dir=temp_dir, name=TEST_MESSAGE_FILE_NAME) as import1,
            TemporaryTestFile(TEST_STATUS_CONTENTS, dir=temp_dir, name=TEST_STATUS_FILE_NAME) as import2,
            TemporaryTestFile(TEST_MODEL_CONTENTS, dir=temp_dir, suffix=AAC_DOCUMENT_EXTENSION) as test_yaml,
        ):
            definitions = parse(test_yaml.name)
            self.assertEqual(len(definitions), 4)

            imports_definition, *_ = collections.get_definitions_by_root_key(ROOT_KEY_IMPORT, definitions)
            import_basenames = [basename(imp) for imp in imports_definition.get_imports()]
            self.assertIn(basename(import1.name), import_basenames)
            self.assertIn(basename(import2.name), import_basenames)

            schema_message_definition = collections.get_definition_by_name(TEST_MESSAGE_NAME, definitions)
            enum_status_definition = collections.get_definition_by_name(TEST_STATUS_NAME, definitions)
            model_echosvc_definition = collections.get_definition_by_name(TEST_MODEL_NAME, definitions)

            self.check_definition(schema_message_definition, TEST_MESSAGE_NAME, ROOT_KEY_SCHEMA)
            self.check_definition(enum_status_definition, TEST_STATUS_NAME, ROOT_KEY_ENUM)
            self.check_definition(model_echosvc_definition, TEST_MODEL_NAME, ROOT_KEY_MODEL)

            self.assertEqual(schema_message_definition.source.uri, import1.name)
            self.assertEqual(enum_status_definition.source.uri, import2.name)
            self.assertEqual(model_echosvc_definition.source.uri, test_yaml.name)

            first, _, third, *_ = imports_definition.lexemes
            self.assertEqual(first.source, test_yaml.name)
            self.assertEqual(first.value, ROOT_KEY_IMPORT)
            self.assertEqual(first.location, SourceLocation(1, 0, 1, 6))

            self.assertEqual(third.source, test_yaml.name)
            self.assertEqual(third.value, f"./{TEST_MESSAGE_FILE_NAME}")
            self.assertEqual(third.location, SourceLocation(3, 6, 24, 2 + len(TEST_MESSAGE_FILE_NAME)))

    def test_handles_multiple_import_sections_per_file(self):
        another_definition = create_enum_definition("TestEnum", ["a", "b", "c"])
        with (
            TemporaryDirectory() as temp_dir,
            TemporaryTestFile(another_definition.to_yaml(), dir=temp_dir, name=TEST_STATUS_FILE_NAME) as import1,
            TemporaryTestFile(TEST_MESSAGE_CONTENTS, dir=temp_dir, name=TEST_MESSAGE_FILE_NAME) as import2,
            TemporaryTestFile(TEST_STATUS_CONTENTS, dir=temp_dir, name=TEST_STATUS_FILE_NAME) as import3,
        ):
            another_import_definition = create_import_definition([import1.name])
            content = f"{another_import_definition.to_yaml()}{YAML_DOCUMENT_SEPARATOR}{TEST_MODEL_CONTENTS}"
            with TemporaryTestFile(content, dir=temp_dir) as main:
                definitions = parse(main.name)
                self.assertEqual(len(definitions), 5)

                import_def_1, import_def_2, *_ = collections.get_definitions_by_root_key(ROOT_KEY_IMPORT, definitions)
                import_basenames = [basename(imp) for imp in import_def_1.get_imports() + import_def_2.get_imports()]
                self.assertIn(basename(import1.name), import_basenames)
                self.assertIn(basename(import2.name), import_basenames)
                self.assertIn(basename(import3.name), import_basenames)

    def test_errors_when_parsing_invalid_yaml(self):
        content = f"{ROOT_KEY_MODEL}: ]["
        with TemporaryTestFile(content) as test_yaml:
            self.check_parser_errors(test_yaml.name, "invalid YAML", content)

    def test_errors_when_parsing_incomplete_model(self):
        content = f"{ROOT_KEY_MODEL}:"
        with TemporaryTestFile(content) as test_yaml:
            self.check_parser_errors(test_yaml.name, "Definition is missing field 'name'", content)

    def test_errors_when_parsing_non_yaml(self):
        content = "not yaml"
        with TemporaryTestFile(content) as test_yaml:
            self.check_parser_errors(test_yaml.name, "not YAML", content)

    def test_content_is_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}"
        parsed_definitions = parse(content, source_uri=PARSER_TEST_SOURCE)

        self.assertEqual(len(parsed_definitions), 2)

        contents = [definition.content for definition in parsed_definitions]
        self.assertIn(TEST_MESSAGE_CONTENTS, contents)
        self.assertIn(f"{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}", contents)

    def test_file_content_is_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}"
        with TemporaryTestFile(content) as test_yaml:
            parsed_definitions = parse(test_yaml.name)

            self.assertEqual(len(parsed_definitions), 2)

            contents = [definition.content for definition in parsed_definitions]
            self.assertIn(TEST_MESSAGE_CONTENTS, contents)
            self.assertIn(f"{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}", contents)

    def test_lexemes_are_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}"
        parsed_definitions = parse(content, source_uri=PARSER_TEST_SOURCE)

        self.assertEqual(len(parsed_definitions), 2)

        self.assertNotIn(
            TEST_STATUS_NAME,
            self.get_lexeme_values_for_definition(TEST_MESSAGE_NAME, parsed_definitions),
        )
        self.assertNotIn(
            TEST_MESSAGE_NAME,
            self.get_lexeme_values_for_definition(TEST_STATUS_NAME, parsed_definitions),
        )

    def test_file_lexemes_are_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}"
        with TemporaryTestFile(content) as test_yaml:
            parsed_definitions = parse(test_yaml.name)

            self.assertEqual(len(parsed_definitions), 2)

            self.assertNotIn(
                TEST_STATUS_NAME,
                self.get_lexeme_values_for_definition(TEST_MESSAGE_NAME, parsed_definitions),
            )
            self.assertNotIn(
                TEST_MESSAGE_NAME,
                self.get_lexeme_values_for_definition(TEST_STATUS_NAME, parsed_definitions),
            )

    def test_does_not_add_doc_separator_if_not_already_present(self):
        definition, *_ = parse(TEST_MESSAGE_CONTENTS, source_uri=PARSER_TEST_SOURCE)
        self.assertEqual(definition.content, TEST_MESSAGE_CONTENTS)

        definitions = parse(
            f"{TEST_MESSAGE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_CONTENTS}", source_uri=PARSER_TEST_SOURCE
        )

        message_definition, *_ = [definition for definition in definitions if definition.name == TEST_MESSAGE_NAME]
        self.assertFalse(message_definition.content.startswith(YAML_DOCUMENT_SEPARATOR))

        status_definition, *_ = [definition for definition in definitions if definition.name == TEST_STATUS_NAME]
        self.assertTrue(status_definition.content.startswith(YAML_DOCUMENT_SEPARATOR))


TEST_MODEL_NAME = "EchoService"
TEST_MESSAGE_NAME = "Message"
TEST_STATUS_NAME = "Status"

TEST_MESSAGE_FILE_NAME = f"{TEST_MESSAGE_NAME}{AAC_DOCUMENT_EXTENSION}"
TEST_STATUS_FILE_NAME = f"{TEST_STATUS_NAME}{AAC_DOCUMENT_EXTENSION}"

TEST_MESSAGE_CONTENTS = f"""
schema:
  name: {TEST_MESSAGE_NAME}
  fields:
  - name: body
    type: string
  - name: sender
    type: string
"""
TEST_STATUS_CONTENTS = f"""
enum:
  name: {TEST_STATUS_NAME}
  values:
    - sent
    - 'failed to send'
"""
TEST_MODEL_CONTENTS = f"""
import:
  files:
    - .{sep}{TEST_MESSAGE_FILE_NAME}
    - {TEST_STATUS_FILE_NAME}
---
model:
  name: {TEST_MODEL_NAME}
  description: This is a message mirror.
  behavior:
    - name: echo
      type: {BEHAVIOR_TYPE_REQUEST_RESPONSE}
      description: This is the one thing it does.
      input:
        - name: inbound
          type: Message
      output:
        - name: outbound
          type: Message
      acceptance:
        - scenario: onReceive
          given:
           - The EchoService is running.
          when:
            - The user sends a message to EchoService.
          then:
            - The user receives the same message from EchoService.
"""
