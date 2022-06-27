from typing import Optional

from tests.helpers.lsp.responses.lsp_response import LspResponse


class HoverResponse(LspResponse):
    def get_content(self) -> Optional[str]:
        return self.response.get("contents")
