from unittest import TestCase

from aac.parser import parse
from aac.validation.ValidatorPlugin import ValidatorPlugin


class TestValidatorPlugin(TestCase):
    def test_from_definition(self):
        definition = parse(TEST_VALIDATION_DEFINITION_STRING)[0]

        expected_result = ValidatorPlugin(name=TEST_VALIDATION_NAME, definition=definition)
        actual_result = ValidatorPlugin.from_definition(definition)

        self.assertEqual(expected_result.name, actual_result.name)
        self.assertEqual(expected_result.definition, actual_result.definition)


TEST_VALIDATION_NAME = "Test Validator"
TEST_VALIDATION_DEFINITION_STRING = f"""
validation:
  name: {TEST_VALIDATION_NAME}
  description: Verifies that every validation definition has a corresponding python plugin implementation
"""
