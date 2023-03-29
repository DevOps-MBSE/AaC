from os.path import lexists
from tempfile import TemporaryDirectory
from unittest import TestCase

from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.first_party.gen_tmgrammar.gen_tmgrammar_impl import (
    JSON_SYNTAX_FILE_NAME,
    PLIST_SYNTAX_FILE_NAME,
    gen_tmgrammar,
)


class TestGenTMGrammar(TestCase):
    def test_gen_tmgrammar_generates_json_syntax_rules_as_default(self):
        with TemporaryDirectory():
            result = gen_tmgrammar()
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
            self.assertRegexpMatches(result.get_messages_as_string(), f"{JSON_SYNTAX_FILE_NAME}.*success")
            self.assertTrue(lexists(JSON_SYNTAX_FILE_NAME))

    def test_gen_tmgrammar_generates_json_syntax_rules(self):
        with TemporaryDirectory():
            result = gen_tmgrammar(json=True, plist=False)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
            self.assertRegexpMatches(result.get_messages_as_string(), f"{JSON_SYNTAX_FILE_NAME}.*success")
            self.assertTrue(lexists(JSON_SYNTAX_FILE_NAME))

    def test_gen_tmgrammar_generates_plist_syntax_rules(self):
        with TemporaryDirectory():
            result = gen_tmgrammar(json=False, plist=True)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
            self.assertRegexpMatches(result.get_messages_as_string(), f"{PLIST_SYNTAX_FILE_NAME}.*success")
            self.assertTrue(lexists(PLIST_SYNTAX_FILE_NAME))
