from unittest import TestCase

from aac import __version__
from aac.cli.builtin_commands.version.version_impl import version

from tests.helpers.assertion import assert_plugin_success


class TestVersion(TestCase):
    def test_version(self):
        result = version()
        assert_plugin_success(result)
        self.assertIn(__version__, "\n".join(result.messages))
