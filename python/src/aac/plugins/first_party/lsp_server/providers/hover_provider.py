"""Module for the Hover Provider which handles all hover requests."""

from typing import Optional

from pygls.lsp.types import MarkupContent, MarkupKind, Hover, HoverParams
from pygls.server import LanguageServer
from pygls.workspace import Document

from aac.lang.definitions.type import remove_list_type_indicator
from aac.plugins.first_party.lsp_server.providers.symbols import get_symbol_at_position
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider


class HoverProvider(LspProvider):
    """Provide useful contextual information for the named item being hovered over."""

    def handle_request(self, language_server: LanguageServer, params: HoverParams) -> Optional[Hover]:
        """Return the YAML representation of the item at the specified position."""
        document: Optional[Document] = language_server.workspace.documents.get(params.text_document.uri)
        position = params.position
        symbol = get_symbol_at_position(document.source, position.line, position.character)

        if symbol is not None:
            name = remove_list_type_indicator(symbol).strip(":")
            definition = language_server.language_context.get_definition_by_name(name)
            return definition and Hover(
                contents=MarkupContent(kind=MarkupKind.Markdown, value=f"```\n{definition.content}\n```")
            )
