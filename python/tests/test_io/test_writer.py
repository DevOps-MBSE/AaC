import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from aac.io.writer import write_definitions_to_file

from tests.helpers.parsed_definitions import create_model_definition


class TestWriter(TestCase):

    def test_write_definitions_to_file(self):
        test_file_name = "out.yaml"

        test_model_name = "TestModel"
        test_model = create_model_definition(test_model_name)

        test_definitions = [test_model]

        with TemporaryDirectory() as temp_dir:
            test_file_uri = os.path.join(temp_dir, test_file_name)
            write_definitions_to_file(test_definitions, test_file_uri)

        with open("r", test_file_uri) as file:
            actual_result = file.read()

        self.assertIn(test_model.to_yaml(), actual_result)
