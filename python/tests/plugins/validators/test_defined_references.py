from unittest import TestCase

from aac.lang import get_active_context
from aac.definition_helpers import get_definitions_by_type
from aac.parser import parse
from aac.plugins.validators.defined_references import get_plugin_aac_definitions, register_validators
from aac.validate import ValidatorPlugin


class TestDefinedReferencesPlugin(TestCase):

    def setUp(self) -> None:
        get_active_context(reload_context=True)

    def test_module_register_validators(self):
        actual_validator_plugin = register_validators()

        validation_definitions = get_definitions_by_type(parse(get_plugin_aac_definitions()), "validation")
        self.assertEqual(1, len(validation_definitions))

        expected_validator_plugin = ValidatorPlugin(name="Type references exist", definition=validation_definitions[0])
        self.assertEqual(expected_validator_plugin.name, actual_validator_plugin.name)
        self.assertEqual(expected_validator_plugin.definition, actual_validator_plugin.definition)

