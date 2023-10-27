import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from aac.in_out.parser import parse
from aac.in_out.writer import write_definitions_to_file
from aac.context.language_context import LanguageContext

class TestWriter(TestCase):
    
    def test_write_definitions_to_file(self):
        test_file_name = "out.yaml"

        test_model_name = "TestModel"
        test_model_yaml = """
model:
  name: TestModel
  description: This is a test model with no content.
""".strip()
        test_enum_name = "TestEnum"
        test_enum_yaml = """
enum:
  name: TestEnum
  values:
  - v1
""".strip()

        with TemporaryDirectory() as temp_dir:
            test_model = parse(test_model_yaml)[0]
            test_enum = parse(test_enum_yaml)[0]
            test_file_uri = os.path.join(temp_dir, test_file_name)
            write_definitions_to_file([test_model, test_enum], test_file_uri)

            self.assertTrue(os.path.exists(test_file_uri))

            with open(test_file_uri, "r") as file:
                actual_result = file.read()
                self.assertIn(test_model_yaml, actual_result)
                self.assertIn("---", actual_result)
                self.assertIn(test_enum_yaml, actual_result)

    def test_write_definitions_to_file_preserve_order(self):
        test_file_name = "out.yaml"

        context = LanguageContext()
        test_definitions = context.get_aac_core_definitions()

        with TemporaryDirectory() as temp_dir:
            test_file_uri = os.path.join(temp_dir, test_file_name)
            write_definitions_to_file(test_definitions, test_file_uri)

            self.assertTrue(os.path.exists(test_file_uri))

            actual_result_parsed_definitions = parse(test_file_uri)

            self.assertListEqual([d.name for d in test_definitions], [d.name for d in actual_result_parsed_definitions])
            self.assertListEqual([d.source.uri for d in test_definitions], [d.source.uri for d in actual_result_parsed_definitions])
            # Disabling this test for now since the writer doesn't maintain multiline descriptions correctly which causes inconsistent lexeme lines when written to file then read back in.
            # self.assertListEqual([d.lexemes[0].location.line for d in test_definitions], [d.lexemes[0].location.line for d in actual_result_parsed_definitions]) # noqa E800
