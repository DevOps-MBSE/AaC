from types import ModuleType
from unittest import TestCase

from aac.execute.plugin_manager import get_plugin_manager, register_plugins_in_package

class TestPluginManager(TestCase):
    def test_plugin_manager(self):
        plugin_manager = get_plugin_manager()
        plugins = plugin_manager.get_plugins()
        plugin = next(iter(plugins))
        name = plugin.plugin_name
        self.assertTrue(str(plugin), ''.join(str(plugins)))

        plugin_manager.unregister(plugin)
        plugins = plugin_manager.get_plugins()
        self.assertNotIn(str(plugin), ''.join(str(plugins)))

        plugin_manager.register(plugin)
        plugins = plugin_manager.get_plugins()
        self.assertTrue(str(plugin), ''.join(str(plugins)))

