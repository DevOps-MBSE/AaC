from typing import Optional

from pygls.lsp.types.basic_structures import Location

from tests.helpers.lsp.responses.lsp_response import LspResponse


class GotoDefinitionResponse(LspResponse):
    def get_location(self) -> Optional[Location]:
        return Location(**self.response[0]) if self.response else None
