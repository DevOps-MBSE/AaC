from typing import Optional

from tests.helpers.lsp.responses.lsp_response import LspResponse


class FindReferencesResponse(LspResponse):
    def get_markdown_content(self) -> Optional[str]:
        return self.response and self.response.get("contents", {}).get("value")

    def get_content(self) -> Optional[str]:
        content = self.get_markdown_content()
        return content and "\n".join(content.splitlines()[1:-1])
