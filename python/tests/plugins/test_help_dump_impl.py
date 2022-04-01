from unittest import TestCase

from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.help_dump.help_dump_impl import help_dump


class TestHelpDump(TestCase):
    def test_help_dump(self):
        result = help_dump()
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
