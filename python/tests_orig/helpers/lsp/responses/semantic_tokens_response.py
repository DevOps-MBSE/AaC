from tests.helpers.lsp.responses.lsp_response import LspResponse


# Refer here to see why 5 is significant:
#  https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_semanticTokens:~:text=relative%27%3B-,Integer%20Encoding%20for%20Tokens
NUM_INTEGERS_TO_ENCODE_TOKEN = 5


class SemanticTokensResponse(LspResponse):
    def get_default_data(self) -> list[int]:
        return self.response.get("data", [])

    def get_semantic_tokens(self) -> list[list[int]]:
        data = self.get_default_data()
        return [data[i:i + NUM_INTEGERS_TO_ENCODE_TOKEN] for i in range(0, len(data), NUM_INTEGERS_TO_ENCODE_TOKEN)]
