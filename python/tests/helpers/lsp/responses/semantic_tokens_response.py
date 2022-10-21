from tests.helpers.lsp.responses.lsp_response import LspResponse


class SemanticTokensResponse(LspResponse):
    def get_default_data(self) -> list[int]:
        return self.response.get("data", [])

    def get_semantic_tokens(self) -> list[list[int]]:
        data = self.get_default_data()
        return [data[i:i + 5] for i in range(0, len(data), 5)]
