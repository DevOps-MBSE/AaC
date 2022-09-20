from typing import Optional
from pygls.lsp.types import WorkspaceEdit
from tests.helpers.lsp.responses.lsp_response import LspResponse


class RenameResponse(LspResponse):
    def get_rename_edits(self) -> WorkspaceEdit:
        return self.response.get("changes")
