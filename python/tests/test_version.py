from unittest import TestCase

from aac import __version__
from aac.cli import _version_cmd

from tests.helpers.assertion import assert_plugin_success


class TestVersion(TestCase):

    def test_version(self):
        result = _version_cmd()
        assert_plugin_success(result)
        self.assertIn(__version__, "\n".join(result.messages))
