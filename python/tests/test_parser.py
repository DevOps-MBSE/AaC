import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from tests.helpers.io import temporary_test_file

from aac.lang import definition_helpers
from aac.parser import parse, get_yaml_from_source
from aac.parser.ParserError import ParserError
from aac.parser.SourceLocation import SourceLocation


class TestArchParser(TestCase):
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
        with temporary_test_file(TEST_IMPORTED_MODEL_FILE_CONTENTS.strip()) as test_yaml:
            parsed_definitions = parse(test_yaml.name)
            self.assertEqual(1, len(parsed_definitions))
            parsed_definition = parsed_definitions[0]

            self.assertGreaterEqual(len(parsed_definition.lexemes), 2)

            first, second, *_ = parsed_definition.lexemes
            self.assertEqual(first.source, test_yaml.name)
            self.assertEqual(first.value, "data")
            self.assertEqual(first.location, SourceLocation(0, 0, 0, 4))

            self.assertEqual(second.source, test_yaml.name)
            self.assertEqual(second.value, "name")
            self.assertEqual(second.location, SourceLocation(1, 2, 8, 4))

    def test_can_handle_string_or_path_sources(self):
        self.assertEqual(TEST_MODEL_FILE, get_yaml_from_source(TEST_MODEL_FILE))

        with temporary_test_file(TEST_MODEL_FILE) as test_yaml:
            self.assertEqual(TEST_MODEL_FILE, get_yaml_from_source(test_yaml.name))

    def test_can_handle_architecture_file_with_imports(self):
        with (
            TemporaryDirectory() as temp_dir,
            temporary_test_file(TEST_IMPORTED_MODEL_FILE_CONTENTS, dir=temp_dir, suffix=".yaml") as import1,
            temporary_test_file(TEST_SECONDARY_IMPORTED_MODEL_FILE_CONTENTS, dir=temp_dir, suffix=".yaml") as import2,
            temporary_test_file(self.get_test_model(import1.name, import2.name), dir=temp_dir) as test_yaml,
        ):

            parsed_models = parse(test_yaml.name)
            data_message_definition = definition_helpers.get_definition_by_name(parsed_models, "Message")
            enum_status_definition = definition_helpers.get_definition_by_name(parsed_models, "Status")
            model_echosvc_definition = definition_helpers.get_definition_by_name(parsed_models, "EchoService")

            self.check_model_name(data_message_definition.definition, "Message", "data")
            self.check_model_name(enum_status_definition.definition, "Status", "enum")
            self.check_model_name(model_echosvc_definition.definition, "EchoService", "model")

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


TEST_IMPORTED_MODEL_FILE_CONTENTS = """
data:
  name: Message
  fields:
  - name: body
    type: string
  - name: sender
    type: string
"""

TEST_SECONDARY_IMPORTED_MODEL_FILE_CONTENTS = """
enum:
  name: Status
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
