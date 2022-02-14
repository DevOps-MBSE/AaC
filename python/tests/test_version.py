from unittest import TestCase

from aac import __version__
from aac.cli import _version_cmd
from aac.plugins.plugin_execution import PluginExecutionStatusCode


class TestVersion(TestCase):

    def test_version(self):
        result = _version_cmd()
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
        self.assertIn(__version__, "\n".join(result.messages))
