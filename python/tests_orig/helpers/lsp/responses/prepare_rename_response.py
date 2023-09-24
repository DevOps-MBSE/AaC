from typing import Optional
from pygls.lsp.types import Range, Position
from tests.helpers.lsp.responses.lsp_response import LspResponse


class PrepareRenameResponse(LspResponse):
    def get_range(self) -> Optional[Range]:
        return_range = None
        if self.response:
            line = self.response.get("start", {}).get("line", 0)
            start_character = self.response.get("start", {}).get("character", 0)
            end_character = self.response.get("end", {}).get("character", 0)
            return_range = Range(
                start=Position(line=line, character=start_character), end=Position(line=line, character=end_character)
            )
        return return_range
