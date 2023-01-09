from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.plugins import PluginError
from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.first_party.plugin_management.plugin_management_impl import list_plugins, activate_plugin, deactivate_plugin

from tests.active_context_test_case import ActiveContextTestCase


class TestPluginManagement(ActiveContextTestCase):
    VALID_PLUGIN_NAME = "gen-json"

    def test_list_plugins(self):
        def plugin_names_to_string(plugins):
            return "\n".join([plugin.name for plugin in plugins])

        result = list_plugins(all=True, active=False, inactive=False)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
        self.assertEqual(result.messages[0], plugin_names_to_string(get_active_context().plugins))

        result = list_plugins(all=False, active=True, inactive=False)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
        self.assertEqual(result.messages[0], plugin_names_to_string(get_active_context().get_active_plugins()))

        result = list_plugins(all=False, active=False, inactive=True)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
        self.assertEqual(result.messages[0], plugin_names_to_string(get_active_context().get_inactive_plugins()))

        result = list_plugins(all=True, active=True, inactive=False)
        self.assertRegexpMatches(result.get_messages_as_string(), "Multiple.*options.*all=True.*active=True")

        result = list_plugins(all=True, active=False, inactive=True)
        self.assertRegexpMatches(result.get_messages_as_string(), "Multiple.*options.*all=True.*inactive=True")

        result = list_plugins(all=False, active=True, inactive=True)
        self.assertRegexpMatches(result.get_messages_as_string(), "Multiple.*options.*active=True.*inactive=True")

        result = list_plugins(all=True, active=True, inactive=True)
        self.assertRegexpMatches(result.get_messages_as_string(), "Multiple.*options.*all=True.*active=True.*inactive=True")

    def test_activate_plugin(self):
        result = activate_plugin(name="not a plugin")
        self.assertEqual(result.status_code, PluginExecutionStatusCode.PLUGIN_FAILURE)

        deactivate_plugin(name=self.VALID_PLUGIN_NAME)
        self.assertIn(self.VALID_PLUGIN_NAME, [plugin.name for plugin in get_active_context().get_inactive_plugins()])
        result = activate_plugin(name=self.VALID_PLUGIN_NAME)
        self.assertIn(self.VALID_PLUGIN_NAME, [plugin.name for plugin in get_active_context().get_active_plugins()])
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_deactivate_plugin(self):
        result = deactivate_plugin(name="not a plugin")
        self.assertEqual(result.status_code, PluginExecutionStatusCode.PLUGIN_FAILURE)

        self.assertIn(self.VALID_PLUGIN_NAME, [plugin.name for plugin in get_active_context().get_active_plugins()])
        result = deactivate_plugin(name=self.VALID_PLUGIN_NAME)
        self.assertIn(self.VALID_PLUGIN_NAME, [plugin.name for plugin in get_active_context().get_inactive_plugins()])
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
