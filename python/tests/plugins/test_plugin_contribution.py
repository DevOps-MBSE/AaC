from unittest.case import TestCase

from aac.plugins.contributions.contribution_type import ContributionType
from aac.plugins.contributions.plugin_contribution import PluginContribution

from tests.helpers.parsed_definitions import create_schema_definition, create_validation_definition
from tests.plugins.test_contribution_points import create_command, create_validation


class TestPluginContribution(TestCase):
    plugin_name = "test_plugin"
    num_items = 2

    def test_can_determine_contribution_types(self):
        contribution = PluginContribution(
            self.plugin_name,
            ContributionType.COMMANDS,
            {create_command(f"test{i}") for i in range(self.num_items)},
        )
        self.assertTrue(contribution.is_contribution_type(ContributionType.COMMANDS))

        contribution = PluginContribution(
            self.plugin_name,
            ContributionType.DEFINITIONS,
            {create_schema_definition(f"test{i}") for i in range(self.num_items)},
        )
        self.assertTrue(contribution.is_contribution_type(ContributionType.DEFINITIONS))

        contribution = PluginContribution(
            self.plugin_name,
            ContributionType.VALIDATIONS,
            {create_validation(f"test{i}", create_validation_definition(f"validation{i}")) for i in range(self.num_items)},
        )
        self.assertTrue(contribution.is_contribution_type(ContributionType.VALIDATIONS))

    def test_hash(self):
        contribution1 = PluginContribution("test", ContributionType.COMMANDS)
        contribution2 = PluginContribution("test", ContributionType.COMMANDS)
        contribution3 = PluginContribution("Test", ContributionType.COMMANDS)
        contribution4 = PluginContribution("test", ContributionType.VALIDATIONS)

        self.assertEqual(contribution1, contribution2)
        self.assertNotEqual(contribution1, contribution3)
        self.assertNotEqual(contribution1, contribution4)
