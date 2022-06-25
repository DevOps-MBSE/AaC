from pygls.lsp.types.basic_structures import Location, LocationLink
from tests.helpers.lsp.responses.lsp_response import LspResponse


class GotoDefinitionResponse(LspResponse):
    def get_location(self) -> Location:
        return Location(**self.response)
