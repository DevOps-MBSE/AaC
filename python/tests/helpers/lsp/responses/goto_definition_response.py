from tests.helpers.lsp.responses.lsp_response import LspResponse


class GotoDefinitionResponse(LspResponse):
    def get_location(self):
        print(self.response)
