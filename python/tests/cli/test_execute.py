from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from aac import __version__ as aac_version
from aac.cli.builtin_commands.version import plugin_command
from aac.cli.execute import cli
from aac.persistence import ACTIVE_CONTEXT_STATE_FILE_NAME

from tests.active_context_test_case import ActiveContextTestCase


class TestExecute(ActiveContextTestCase):
    @patch("aac.lang.language_context.LanguageContext.export_to_file")
    def test_version_command(self, export_to_file: MagicMock):
        runner = CliRunner()
        result = runner.invoke(cli, [plugin_command])
        export_to_file.assert_called_once_with(ACTIVE_CONTEXT_STATE_FILE_NAME)
        self.assertIn(aac_version, result.output)
