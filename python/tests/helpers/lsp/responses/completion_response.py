from typing import Optional
from pygls.lsp.types.language_features.completion import CompletionItem
from tests.helpers.lsp.responses.lsp_response import LspResponse


class CompletionResponse(LspResponse):
    def get_completion_items(self) -> list[CompletionItem]:
        return self.response.get("items")

    def get_completion_item_by_label(self, label: str) -> Optional[CompletionItem]:
        items = [item for item in self.get_completion_items() if item.get("label") == label]
        return items[0] if items else None
