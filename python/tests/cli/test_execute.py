import io
import sys
from unittest import TestCase
from unittest.mock import patch

from aac import __version__ as aac_version
from aac.cli.execute import run_cli
from aac.lang.active_context_lifecycle_manager import get_active_context


class TestExecute(TestCase):
    def setUp(self):
        get_active_context(reload_context=True)

    @patch('argparse._sys.argv', ['aac', 'version'])
    def test_run_cli_version_command(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        run_cli()
        sys.stdout = sys.__stdout__
        result_string = captured_output.getvalue()

        self.assertIn('success', result_string)
        self.assertIn(aac_version, result_string)
