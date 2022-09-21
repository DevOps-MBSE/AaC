from typing import Optional
from pygls.lsp.types import WorkspaceEdit
from tests.helpers.lsp.responses.lsp_response import LspResponse


class RenameResponse(LspResponse):
    def get_rename_edits(self) -> Optional[WorkspaceEdit]:
        return_value = None
        if self.response:
            return_value = self.response.get("changes")
        return return_value
