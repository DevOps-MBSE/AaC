from unittest import TestCase
from aac.lang.ActiveContextClass import ActiveContext

from aac.lang.context_manager import get_active_context
from aac.plugins import get_plugin_definitions
from aac.spec import get_aac_spec


class TestContextManager(TestCase):
    def test_init_active_context(self):

        active_context_parsed_definitions = get_active_context().context_definitions

        # Assert that the initialized context has more definitions than a new, unmanaged context
        self.assertGreater(len(active_context_parsed_definitions), len(ActiveContext().context_definitions))

        core_spec_definitions = get_aac_spec()
        plugin_definitions = get_plugin_definitions()

        core_spec_definition_count = len(core_spec_definitions)
        plugin_definition_count = len(plugin_definitions)

        self.assertEqual(len(active_context_parsed_definitions), core_spec_definition_count + plugin_definition_count)
