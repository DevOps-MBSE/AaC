from unittest import TestCase

from aac import parser
from aac.plugins.validators.validation_module import get_plugin_aac_definitions, register_validators
from aac.validation.ValidatorPlugin import ValidatorPlugin


class TestValidationModule(TestCase):

    def test_validation_module_register_validators(self):
        actual_validator_plugin = register_validators()
        expected_validator_plugin = ValidatorPlugin(name="Definition has an implementation", validation_definition=self.get_parsed_validation_definitions())
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugin.name)
        self.assertEqual(expected_validator_plugin.validation_definition, actual_validator_plugin.validation_definition)

    def get_parsed_validation_definitions(self):
        parsed_models = parser.parse_str(__name__, get_plugin_aac_definitions())

        for parsed_model in parsed_models:
            if "validation" in parsed_models[parsed_model]:
                return parsed_models[parsed_model]
