from unittest import TestCase

from aac.execute.plugin_manager import get_plugin_manager


class TestPluginManager(TestCase):
    def test_plugin_manager(self):
        plugin_manager = get_plugin_manager()
        plugins = plugin_manager.get_plugins()
        plugin = next(iter(plugins))
        self.assertTrue(str(plugin), msg=''.join(str(plugins)))

        plugin_manager.unregister(plugin)
        plugins = plugin_manager.get_plugins()
        self.assertNotIn(str(plugin), ''.join(str(plugins)))

        plugin_manager.register(plugin)
        plugins = plugin_manager.get_plugins()
        self.assertTrue(str(plugin), msg=''.join(str(plugins)))

# More investigations for allowing a fail test with pluggy required.  It currently accepts any type, so a fail test is not clear.
