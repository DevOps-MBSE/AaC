from unittest import TestCase

from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.first_party.gen_tmgrammar.gen_tmgrammar_impl import gen_tmgrammar


class TestGenTMGrammar(TestCase):
    def test_gen_tmgrammar(self):
        # TODO: Write tests for gen_tmgrammar

        json = bool()
        plist = bool()

        result = gen_tmgrammar(json=json, plist=plist)
        self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
