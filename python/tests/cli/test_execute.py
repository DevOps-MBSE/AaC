from click.testing import CliRunner

from aac import __version__ as aac_version
from aac.cli.builtin_commands.version import plugin_command
from aac.cli.execute import cli

from tests.active_context_test_case import ActiveContextTestCase


class TestExecute(ActiveContextTestCase):
    def test_version_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, [plugin_command])
        self.assertIn(aac_version, result.output)
