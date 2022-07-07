"""Module for the Hover Provider which handles all hover requests."""

from typing import Optional

from pygls.lsp.types.language_features.hover import Hover, HoverParams
from pygls.server import LanguageServer
from pygls.workspace import Document

from aac.lang.lsp.providers.lsp_provider import LspProvider


class HoverProvider(LspProvider):
    """Provide useful contextual information for the named item being hovered over."""

    def handle_request(self, ls: LanguageServer, params: HoverParams) -> Optional[Hover]:
        """Return the YAML representation of the item at the specified position."""
        document: Optional[Document] = ls.workspace.documents.get(params.text_document.uri)
        name = document.word_at_position(params.position) if document else ""
        definition = ls.language_context.get_definition_by_name(name)
        return definition and Hover(contents=definition.content)
