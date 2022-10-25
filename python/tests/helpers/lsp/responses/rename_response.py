from typing import Optional
from pygls.lsp.types import WorkspaceEdit, TextEdit
from tests.helpers.lsp.responses.lsp_response import LspResponse


class RenameResponse(LspResponse):
    def get_workspace_edit(self) -> Optional[WorkspaceEdit]:
        return_value = None
        if self.response:
            return_value = self.response.get("changes")
        return return_value

    def get_all_text_edits(self) -> list[TextEdit]:
        return_value = []
        if self.response:
            edit_lists = list(self.response.get("changes").values())
            return_value = [edit for edits_list in edit_lists for edit in edits_list]

        return return_value
