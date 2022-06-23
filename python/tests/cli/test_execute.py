import io
import sys
from unittest.mock import patch

from aac import __version__ as aac_version
from aac.cli.execute import run_cli

from tests.active_context_test_case import ActiveContextTestCase


class TestExecute(ActiveContextTestCase):
    @patch('argparse._sys.argv', ['aac', 'version'])
    def test_run_cli_version_command(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        run_cli()
        sys.stdout = sys.__stdout__
        result_string = captured_output.getvalue()

        self.assertIn('success', result_string)
        self.assertIn(aac_version, result_string)
