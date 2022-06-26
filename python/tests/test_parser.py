import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from aac.lang import definition_helpers
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.source_location import SourceLocation
from aac.parser import parse, ParserError
from aac.parser._parse_source import YAML_DOCUMENT_SEPARATOR, _add_yaml_document_separator

from tests.helpers.io import temporary_test_file


class TestParser(TestCase):
    def get_lexeme_values_for_definition(self, name: str, definitions: list[Definition]) -> list[str]:
        lexemes = [definition.lexemes for definition in definitions if definition.name == name][0]
        return [lexeme.value for lexeme in lexemes]

    def get_test_model(self, import1: str = "a.yaml", import2: str = "b.yaml"):
        return TEST_MODEL_FILE.format(os.path.basename(import1), os.path.basename(import2)).strip()

    def check_model_name(self, model, name, type):
        self.assertIsNotNone(model.get(type))
        self.assertIsNotNone(model.get(type).get("name"))
        self.assertEqual(name, model.get(type).get("name"))

    def check_parser_errors(self, filespec: str, *error_messages: list[str]):
        with self.assertRaises(ParserError) as cm:
            parse(filespec)

        # Assert that each error message is contained in the returned error message string.
        errors = "\n".join(cm.exception.errors)
        list(map(lambda e: self.assertIn(e, errors), error_messages))
        self.assertEqual(cm.exception.source, filespec)

    def test_can_get_lexemes_from_parsed_architecture_file(self):
        with temporary_test_file(TEST_MESSAGE_FILE_CONTENTS.strip()) as test_yaml:
            parsed_definitions = parse(test_yaml.name)
            self.assertEqual(1, len(parsed_definitions))
            parsed_definition = parsed_definitions[0]

            self.assertGreaterEqual(len(parsed_definition.lexemes), 2)

            first, second, *_ = parsed_definition.lexemes
            self.assertEqual(first.source, test_yaml.name)
            self.assertEqual(first.value, "schema")
            self.assertEqual(first.location, SourceLocation(0, 0, 0, 6))

            self.assertEqual(second.source, test_yaml.name)
            self.assertEqual(second.value, "name")
            self.assertEqual(second.location, SourceLocation(1, 2, 10, 4))

    def test_can_handle_architecture_file_with_imports(self):
        with (
            TemporaryDirectory() as temp_dir,
            temporary_test_file(TEST_MESSAGE_FILE_CONTENTS, dir=temp_dir, suffix=".aac") as import1,
            temporary_test_file(TEST_STATUS_FILE_CONTENTS, dir=temp_dir, suffix=".aac") as import2,
            temporary_test_file(self.get_test_model(import1.name, import2.name), dir=temp_dir, suffix=".aac") as test_yaml,
        ):

            parsed_models = parse(test_yaml.name)

            self.assertEqual(len(parsed_models), 3)

            schema_message_definition = definition_helpers.get_definition_by_name("Message", parsed_models)
            enum_status_definition = definition_helpers.get_definition_by_name("Status", parsed_models)
            model_echosvc_definition = definition_helpers.get_definition_by_name("EchoService", parsed_models)

            self.check_model_name(schema_message_definition.structure, "Message", "schema")
            self.check_model_name(enum_status_definition.structure, "Status", "enum")
            self.check_model_name(model_echosvc_definition.structure, "EchoService", "model")

            # For some reason MacOS prepends /private to temporary files/directories
            self.assertEqual(schema_message_definition.source.uri.removeprefix("/private"), import1.name)
            self.assertEqual(enum_status_definition.source.uri.removeprefix("/private"), import2.name)
            self.assertEqual(model_echosvc_definition.source.uri.removeprefix("/private"), test_yaml.name)

            first, second, *_ = model_echosvc_definition.lexemes
            self.assertEqual(first.source, test_yaml.name)
            self.assertEqual(first.value, "import")
            self.assertEqual(first.location, SourceLocation(0, 0, 0, 6))

            import1_basename = os.path.basename(import1.name)
            self.assertEqual(second.source, test_yaml.name)
            self.assertEqual(second.value, f"./{import1_basename}")
            self.assertEqual(second.location, SourceLocation(1, 4, 12, 2 + len(import1_basename)))

    def test_errors_when_parsing_invalid_yaml(self):
        content = "model: ]["
        with temporary_test_file(content) as test_yaml:
            self.check_parser_errors(test_yaml.name, "invalid YAML", content)

    def test_errors_when_parsing_incomplete_model(self):
        content = "model:"
        with temporary_test_file(content) as test_yaml:
            self.check_parser_errors(test_yaml.name, "incomplete model", content)

    def test_errors_when_parsing_non_yaml(self):
        content = "not yaml"
        with temporary_test_file(content) as test_yaml:
            self.check_parser_errors(test_yaml.name, "not YAML", content)

    def test_content_is_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_FILE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_FILE_CONTENTS}"
        parsed_definitions = parse(content, source_uri="<parser test>")

        self.assertEqual(len(parsed_definitions), 2)

        contents = [definition.content for definition in parsed_definitions]
        self.assertIn(TEST_MESSAGE_FILE_CONTENTS, contents)
        self.assertIn(_add_yaml_document_separator(TEST_STATUS_FILE_CONTENTS), contents)

    def test_file_content_is_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_FILE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_FILE_CONTENTS}"
        with temporary_test_file(content) as test_yaml:
            parsed_definitions = parse(test_yaml.name)

            self.assertEqual(len(parsed_definitions), 2)

            contents = [definition.content for definition in parsed_definitions]
            self.assertIn(TEST_MESSAGE_FILE_CONTENTS, contents)
            self.assertIn(_add_yaml_document_separator(TEST_STATUS_FILE_CONTENTS), contents)

    def test_lexemes_are_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_FILE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_FILE_CONTENTS}"
        parsed_definitions = parse(content, source_uri="<parser test>")

        self.assertEqual(len(parsed_definitions), 2)

        self.assertNotIn(TEST_STATUS_FILE_CONTENTS_NAME, self.get_lexeme_values_for_definition(TEST_MESSAGE_FILE_CONTENTS_NAME, parsed_definitions))
        self.assertNotIn(TEST_MESSAGE_FILE_CONTENTS_NAME, self.get_lexeme_values_for_definition(TEST_STATUS_FILE_CONTENTS_NAME, parsed_definitions))

    def test_file_lexemes_are_split_by_yaml_documents(self):
        content = f"{TEST_MESSAGE_FILE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_FILE_CONTENTS}"
        with temporary_test_file(content) as test_yaml:
            parsed_definitions = parse(test_yaml.name)

            self.assertEqual(len(parsed_definitions), 2)

            self.assertNotIn(TEST_STATUS_FILE_CONTENTS_NAME, self.get_lexeme_values_for_definition(TEST_MESSAGE_FILE_CONTENTS_NAME, parsed_definitions))
            self.assertNotIn(TEST_MESSAGE_FILE_CONTENTS_NAME, self.get_lexeme_values_for_definition(TEST_STATUS_FILE_CONTENTS_NAME, parsed_definitions))

    def test_does_not_add_doc_separator_if_not_already_present(self):
        definition, *_ = parse(TEST_MESSAGE_FILE_CONTENTS, source_uri="<parser test>")
        self.assertEqual(definition.content, TEST_MESSAGE_FILE_CONTENTS)

        definitions = parse(f"{TEST_MESSAGE_FILE_CONTENTS}{YAML_DOCUMENT_SEPARATOR}{TEST_STATUS_FILE_CONTENTS}", source_uri="<parser test>")

        message_definition, *_ = [definition for definition in definitions if definition.name == TEST_MESSAGE_FILE_CONTENTS_NAME]
        self.assertFalse(message_definition.content.startswith(YAML_DOCUMENT_SEPARATOR))

        status_definition, *_ = [definition for definition in definitions if definition.name == TEST_STATUS_FILE_CONTENTS_NAME]
        self.assertTrue(status_definition.content.startswith(YAML_DOCUMENT_SEPARATOR))


TEST_MESSAGE_FILE_CONTENTS_NAME = "Message"
TEST_STATUS_FILE_CONTENTS_NAME = "Status"
TEST_MESSAGE_FILE_CONTENTS = f"""
schema:
  name: {TEST_MESSAGE_FILE_CONTENTS_NAME}
  fields:
  - name: body
    type: string
  - name: sender
    type: string
"""
TEST_STATUS_FILE_CONTENTS = f"""
enum:
  name: {TEST_STATUS_FILE_CONTENTS_NAME}
  values:
    - sent
    - 'failed to send'
"""
TEST_MODEL_FILE = """
import:
  - ./{}
  - {}
model:
  name: EchoService
  description: This is a message mirror.
  behavior:
    - name: echo
      type: request-response
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
