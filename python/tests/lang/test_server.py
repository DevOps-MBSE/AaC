from pygls.lsp import methods
from pygls.lsp.types import Hover, HoverParams, Position
from pygls.lsp.types.language_features.completion import CompletionContext, CompletionParams, CompletionTriggerKind

from tests.lang.base_lsp_test_case import BaseLspTestCase


class TestLspServer(BaseLspTestCase):
    def test_handles_hover_request(self):
        res: Hover = self.send_request(
            methods.HOVER,
            HoverParams(
                text_document={"uri": self.get_document("test.aac")},
                position=Position(line=0, character=0),
            ),
        )

        self.assertSequenceEqual(list(res.keys()), ["contents"])
        self.assertIn("LSP server", res.get("contents"))
