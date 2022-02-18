from tempfile import TemporaryDirectory
from unittest import TestCase

from aac.util import new_working_dir
from tests.util import temporary_test_file

from aac import parser


class TestArchParser(TestCase):
    def write_test_file(self, name, content):
        with open(name, "w") as test_file:
            test_file.write(content)
        return name

    def check_model_name(self, model, name, type):
        self.assertIsNotNone(model.get(name))
        self.assertIsNotNone(model.get(name).get(type))
        self.assertEqual(name, model.get(name).get(type).get("name"))

    def check_parser_errors(self, filespec: str, *error_messages: list[str]):
        with self.assertRaises(parser.ParserError) as cm:
            parser.parse_file(filespec)

        # Assert that each error message is contained in the returned error message string.
        errors = "\n".join(cm.exception.errors)
        list(map(lambda e: self.assertIn(e, errors), error_messages))
        self.assertEqual(cm.exception.source, filespec)

    def test_can_parse_architecture_model_string(self):
        model = parser.parse_str("parser-test", TEST_IMPORTED_MODEL_FILE_CONTENTS)

        self.check_model_name(model, "Message", "data")

    def test_can_parse_architecture_model_string_with_imports(self):
        model = parser.parse_str("parser-test", TEST_MODEL_FILE)

        self.check_model_name(model, "EchoService", "model")

    def test_can_parse_architecture_model_from_file(self):
        with TemporaryDirectory() as tmpdir, new_working_dir(tmpdir):
            self.write_test_file("Message.yaml", TEST_IMPORTED_MODEL_FILE_CONTENTS)
            self.write_test_file("Status.yaml", TEST_SECONDARY_IMPORTED_MODEL_FILE_CONTENTS)
            model_file = self.write_test_file("EchoService.yaml", TEST_MODEL_FILE)

            model = parser.parse_file(model_file)

            self.check_model_name(model, "Message", "data")
            self.check_model_name(model, "Status", "enum")
            self.check_model_name(model, "EchoService", "model")

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
  - ./Message.yaml
  - Status.yaml
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
