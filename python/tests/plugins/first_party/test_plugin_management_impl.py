from unittest import TestCase

from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.first_party.plugin_management.plugin_management_impl import list_plugins, activate_plugin, deactivate_plugin


class TestPluginManagement(TestCase):
    def test_list_plugins(self):
        all = bool()
        active = bool()
        inactive = bool()

        result = list_plugins(all=all, active=active, inactive=inactive)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_activate_plugin(self):
        plugin_name = str()

        result = activate_plugin(plugin_name=plugin_name)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

    def test_deactivate_plugin(self):
        plugin_name = str()

        result = deactivate_plugin(plugin_name=plugin_name)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
