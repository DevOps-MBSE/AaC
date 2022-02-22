from unittest import TestCase
from unittest.mock import patch

from aac.lang.server import start_lsp
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

from tests.lang.LspTestClient import LspTestClient


class TestLspServer(TestCase):
    def setUp(self):
        self.client = LspTestClient()
        self.client.start()
        res = self.client.send_request(
            methods.INITIALIZE,
            InitializeParams(process_id=12345, root_uri="file://", capabilities=ClientCapabilities()),
        )

        self.assertIn("capabilities", res)

    def tearDown(self):
        self.client.stop()

    @patch("aac.lang.server.server")
    def test_starts_io_server_when_not_in_dev_mode(self, server):
        result = start_lsp(dev=False)
        self.assertTrue(result.is_success())
        self.assertTrue(server.start_io.called)

    def test_handles_hover_request(self):
        res: Hover = self.client.send_request(
            methods.HOVER,
            HoverParams(text_document={"uri": TEST_DOCUMENT_URI}, position=Position(line=0, character=0)),
        )

        self.assertSequenceEqual(list(res.keys()), ["contents"])
        self.assertIn("LSP server", res.get("contents"))

    def test_handles_completion_request(self):
        res: list[CompletionItem] = self.client.send_request(
            methods.COMPLETION,
            CompletionParams(text_document={"uri": TEST_DOCUMENT_URI}, position=Position(line=0, character=0)),
        )

        self.assertSequenceEqual(list(res.keys()), ["isIncomplete", "items"])
        self.assertSequenceEqual([i.get("label") for i in res.get("items")], get_roots())
        self.assertFalse(res.get("isIncomplete"))


TEST_DOCUMENT_URI = uris.from_fs_path(__file__)
