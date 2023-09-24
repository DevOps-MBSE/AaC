from unittest import TestCase

from aac.plugins.validators import get_validation_definition_from_plugin_yaml


class TestValidatorsModule(TestCase):

    def test_get_validation_definition_from_plugin_definitions(self):
        parsed_definition = get_validation_definition_from_plugin_yaml(TEST_VALIDATION_DEFINITION_STRING)
        self.assertEqual(TEST_VALIDATION_NAME, parsed_definition.name)


TEST_VALIDATION_NAME = "Test Validator"
TEST_VALIDATION_DEFINITION_STRING = f"""
validation:
  name: {TEST_VALIDATION_NAME}
  description: Verifies that every validation definition has a corresponding python plugin implementation
"""
