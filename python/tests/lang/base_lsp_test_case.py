from unittest import TestCase

from pygls.lsp import methods
from pygls.lsp.types import ClientCapabilities, InitializeParams

from tests.lang.lsp_test_client import LspTestClient

class BaseLspTestCase(TestCase):
    """Base test case providing set up and tear down for LSP tests."""

    def setUp(self) -> None:
        super().setUp()

        self.client = LspTestClient()
        self.client.start()
        res = self.client.send_request(
            methods.INITIALIZE,
            InitializeParams(
                process_id=12345, root_uri="file://", capabilities=ClientCapabilities()
            ),
        )

        self.assertIn("capabilities", res)

    def tearDown(self):
        self.client.stop()
