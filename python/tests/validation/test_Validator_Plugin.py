from unittest import TestCase

from aac import parser
from aac.validation.ValidatorPlugin import ValidatorPlugin


class TestValidatorPlugin(TestCase):
    def test_from_definition(self):
        definition = parser.parse_str("validator_plugin_tests", TEST_VALIDATION_DEFINITION_STRING)

        expected_result = ValidatorPlugin(name=TEST_VALIDATION_NAME, validation_definition=definition.get(TEST_VALIDATION_NAME))
        actual_result = ValidatorPlugin.from_definition(definition.get(TEST_VALIDATION_NAME))

        self.assertEqual(expected_result.name, actual_result.name)
        self.assertEqual(expected_result.validation_definition, actual_result.validation_definition)


TEST_VALIDATION_NAME = "Test Validator"
TEST_VALIDATION_DEFINITION_STRING = f"""
validation:
  name: {TEST_VALIDATION_NAME}
  description: Verifies that every validation definition has a corresponding python plugin implementation
"""
