from unittest import TestCase
from aac.lang.language_context import LanguageContext

from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins.plugin_manager import get_plugin_definitions
from aac.spec import get_aac_spec


class TestActiveContextLifecycleManager(TestCase):
    def test_init_active_context(self):

        active_context_parsed_definitions = get_active_context(reload_context=True).definitions

        # Assert that the initialized context has more definitions than a new, unmanaged context
        self.assertGreater(len(active_context_parsed_definitions), len(LanguageContext().definitions))

        core_spec_definitions = get_aac_spec()
        plugin_definitions = get_plugin_definitions()

        core_spec_definition_count = len(core_spec_definitions)
        plugin_definition_count = len(plugin_definitions)

        self.assertEqual(len(active_context_parsed_definitions), core_spec_definition_count + plugin_definition_count)
