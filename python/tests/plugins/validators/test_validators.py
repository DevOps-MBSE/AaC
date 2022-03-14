from unittest import TestCase

from aac.plugins.validators import get_validation_definition_from_plugin_definitions


class TestValidationModule(TestCase):
    def test_get_validation_definition_from_plugin_definitions(self):
        parsed_definition = get_validation_definition_from_plugin_definitions(__name__, TEST_VALIDATION_DEFINITION_STRING)
        definition = parsed_definition.get("validation")
        definition_name = definition.get("name")
        self.assertEqual(TEST_VALIDATION_NAME, definition_name)


TEST_VALIDATION_NAME = "Test Validator"
TEST_VALIDATION_DEFINITION_STRING = f"""
validation:
  name: {TEST_VALIDATION_NAME}
  description: Verifies that every validation definition has a corresponding python plugin implementation
"""
