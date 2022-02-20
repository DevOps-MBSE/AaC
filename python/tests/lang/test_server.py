from unittest import TestCase
from unittest.mock import patch

from aac.lang.server import default_host, default_port, start_lsp
from aac.spec.core import get_roots
from pygls import uris
from pygls.lsp import methods
from pygls.lsp.types import (
    ClientCapabilities,
    CompletionItem,
    CompletionParams,
    Hover,
    HoverParams,
    InitializeParams,
    Position,
)

from .configure_test import LspTestClient, default_timeout


class TestLspServer(TestCase):
    def setUp(self):
        self.client = LspTestClient()
        self.client.start()
        res = self.client.client.lsp.send_request(
            methods.INITIALIZE,
            InitializeParams(process_id=12345, root_uri="file://", capabilities=ClientCapabilities()),
        ).result(timeout=default_timeout)

        self.assertIn("capabilities", res)

    def tearDown(self):
        self.client.stop()

    @patch("aac.lang.server.server")
    def test_starts_tcp_server_with_default_host_and_port(self, server):
        result = start_lsp(dev=True)
        self.assertTrue(result.is_success())
        self.assertTrue(server.start_tcp.called_with(default_host, default_port))

    @patch("aac.lang.server.server")
    def test_starts_tcp_server_with_custom_host_and_port(self, server):
        host, port = "host", 123
        result = start_lsp(host, port, True)
        self.assertTrue(result.is_success())
        self.assertTrue(server.start_tcp.called_with(host, port))

    @patch("aac.lang.server.server")
    def test_starts_io_server_when_not_in_dev_mode(self, server):
        result = start_lsp(dev=False)
        self.assertTrue(result.is_success())
        self.assertTrue(server.start_io.called)

    def test_handles_hover_request(self):
        res: Hover = self.client.client.lsp.send_request(
            methods.HOVER,
            HoverParams(text_document={"uri": TEST_DOCUMENT_URI}, position=Position(line=0, character=0)),
        ).result(timeout=default_timeout)

        self.assertSequenceEqual(list(res.keys()), ["contents"])
        self.assertIn("LSP server", res.get("contents"))

    def test_handles_completion_request(self):
        res: list[CompletionItem] = self.client.client.lsp.send_request(
            methods.COMPLETION,
            CompletionParams(text_document={"uri": TEST_DOCUMENT_URI}, position=Position(line=0, character=0)),
        ).result(timeout=default_timeout)

        self.assertSequenceEqual(list(res.keys()), ["isIncomplete", "items"])
        self.assertSequenceEqual([i.get("label") for i in res.get("items")], get_roots())
        self.assertFalse(res.get("isIncomplete"))


TEST_DOCUMENT = """
data:
  name: test data
  fields:
    - name: alpha
      type: string
    - name: beta
      type: string
    - name: gamma
      type: string
  required:
    - alpha
    - beta
"""

TEST_DOCUMENT_URI = uris.from_fs_path(__file__)
