from typing import Optional
from unittest import TestCase

from pygls import uris
from pygls.lsp import methods
from pygls.lsp.types import ClientCapabilities, InitializeParams
from pygls.lsp.types.basic_structures import Model

from tests.lang.lsp_test_client import LspTestClient, DEFAULT_TIMEOUT_IN_SECONDS


class BaseLspTestCase(TestCase):
    """Base test case providing set up and tear down for LSP tests."""

    def setUp(self) -> None:
        super().setUp()

        self.client = LspTestClient()
        self.client.start()
        res = self.client.send_request(
            methods.INITIALIZE,
            InitializeParams(
                process_id=12345, root_uri=self.get_document("root.aac"), capabilities=ClientCapabilities()
            ),
        )

        self.assertIn("capabilities", res)

    def tearDown(self):
        self.client.stop()

    def get_document(self, file_name: str) -> Optional[str]:
        """Return a virtual document URI."""
        return uris.from_fs_path(file_name)

    def send_request(self, method: str, params: Optional[Model] = None, timeout: int = DEFAULT_TIMEOUT_IN_SECONDS):
        """
        Send an LSP request to the server via the LSP test client.

        Args:
            method (str): The LSP method to use for the request.
            params (Model): The parameters to send with the request. (optional)
            timeout (int): The timeout to use when waiting for a result. If not provided, DEFAULT_TIMEOUT_IN_SECONDS is used.

        Returns:
            The LSP response for the sent request.
        """
        return self.client.send_request(method, params, timeout)

    def send_notification(self, method: str):
        """
        Send an LSP notification to the server via the LSP test client.

        Args:
            method (str): The LSP method to use for the notification.

        Returns:
            The LSP response for the sent notification.
        """
        return self.client.send_notification(method)
