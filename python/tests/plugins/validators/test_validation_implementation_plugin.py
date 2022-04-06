from unittest import TestCase

from aac.lang.definition_helpers import get_definitions_by_root_key
from aac.parser import parse
from aac.plugins.validators.validator_implementation import get_plugin_aac_definitions, register_validators
from aac.plugins.validators import ValidatorPlugin


class TestValidationImplementPlugin(TestCase):

    def test_validation_module_register_validators(self):
        actual_validator_plugin = register_validators()

        validation_definitions = get_definitions_by_root_key("validation", parse(get_plugin_aac_definitions()))
        self.assertEqual(1, len(validation_definitions))

        expected_validator_plugin = ValidatorPlugin(name="Validation definition has an implementation", definition=validation_definitions[0], validation_function=(lambda x: x))
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugin.name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugin.definition)
