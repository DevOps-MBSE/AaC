from unittest import TestCase

from aac.lang.definition_helpers import get_definitions_by_type
from aac.parser import parse
from aac.plugins.validators.validator_implementation import get_plugin_aac_definitions, register_validators
from aac.validate import ValidatorPlugin


class TestValidationImplementPlugin(TestCase):

    def test_validation_module_register_validators(self):
        actual_validator_plugin = register_validators()

        validation_definitions = get_definitions_by_type(parse(get_plugin_aac_definitions()), "validation")
        self.assertEqual(1, len(validation_definitions))

        expected_validator_plugin = ValidatorPlugin(name="Validation definition has an implementation", definition=validation_definitions[0])
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugin.name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugin.definition)
