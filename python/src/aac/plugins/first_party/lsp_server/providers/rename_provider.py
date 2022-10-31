"""Module for the Rename Provider which handles requests to rename symbols."""

import logging
from typing import Optional
from pygls.server import LanguageServer
from pygls.lsp.types import Position, RenameParams, WorkspaceEdit, TextEdit, TextDocumentIdentifier
from pygls.workspace import Document

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.references import get_definition_type_references_from_list, get_enum_references_from_context
from aac.lang.definitions.type import remove_list_type_indicator
from aac.lang.definitions.lexeme import Lexeme
from aac.plugins.first_party.lsp_server.providers.symbols import (
    get_symbol_at_position,
    get_possible_symbol_types,
    SymbolType,
)
from aac.plugins.first_party.lsp_server.providers.locations import get_location_from_lexeme
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider


class RenameProvider(LspProvider):
    """Handles the rename requests."""

    def handle_request(self, language_server: LanguageServer, params: RenameParams) -> WorkspaceEdit:
        """Return the workspace edit consisting of text edits for the rename request."""
        self.language_server = language_server
        return self.get_rename_edits(
            self.language_server.workspace.documents, params.text_document.uri, params.position, params.new_name
        )

    def get_rename_edits(
        self, documents: dict[str, Document], current_uri: str, position: Position, new_name: str
    ) -> Optional[WorkspaceEdit]:
        """
        Return the rename edits for the selected symbol.

        https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_rename

        Args:
            documents (dict[str, Document]): A container mapping document names to the associated LSP document.
            current_uri (str): The URI of the file that's currently active.
            position (Position): The position of the cursor in `current_uri` whose definition is being searched.
            new_name (str): The new name to replace instances of the selected symbol with.

        Returns:
            A workspace edit consisting of the text edits spanning all pertinent instances of the selected symbol, or None.
        """
        document = documents.get(current_uri)
        workspace_edit = None

        if document:
            symbol = get_symbol_at_position(document.source, position.line, position.character)
            edits = self._get_rename_edits(symbol, new_name) if symbol else {}

            if symbol:
                try:
                    workspace_edit = WorkspaceEdit(text_document=TextDocumentIdentifier(uri=document.uri), changes=edits)
                except Exception as error:
                    logging.error(error)

        return workspace_edit

    def _get_rename_edits(self, symbol: str, new_name: str) -> dict[str, TextEdit]:
        """Returns the list of text edits based on the selected symbol's type."""
        if not symbol:
            return None

        language_context = self.language_server.language_context

        name = remove_list_type_indicator(symbol).strip(":")
        symbol_types = get_possible_symbol_types(name, language_context)

        edits = {}
        if SymbolType.DEFINITION_NAME in symbol_types:
            definition_to_find = language_context.get_definition_by_name(name)
            if not definition_to_find:
                logging.warn(f"Can't find references for non-definition {name}")
            else:
                edits = self._get_definition_name_text_edits(new_name, definition_to_find, language_context)

        if SymbolType.ENUM_VALUE_TYPE in symbol_types:
            enum_to_find = language_context.get_enum_definition_by_type(name)
            if not enum_to_find:
                logging.warn(f"Can't find references for non-enum {name}")
            else:
                edits = self._get_enum_value_type_text_edits(name, new_name, enum_to_find, language_context)

        return edits

    def _get_definition_name_text_edits(
        self, new_name: str, definition_to_find: Definition, language_context: LanguageContext
    ) -> dict[str, TextEdit]:
        """Returns a dictionary of document uri to TextEdits where the uri is the key and the list of edits the value."""
        edits = {}
        definition_references = get_definition_type_references_from_list(definition_to_find, language_context.definitions)
        definitions_to_alter = [*definition_references, definition_to_find]

        for definition in definitions_to_alter:

            def filter_lexeme_by_reference_name(lexeme: Lexeme) -> bool:
                return remove_list_type_indicator(lexeme.value) == definition_to_find.name

            reference_lexemes = filter(filter_lexeme_by_reference_name, definition.lexemes)

            for lexeme_to_replace in reference_lexemes:
                document_edits = edits.get(lexeme_to_replace.source, [])
                replacement_range = get_location_from_lexeme(lexeme_to_replace).range
                document_edits.append(TextEdit(range=replacement_range, new_text=new_name))
                edits[str(lexeme_to_replace.source)] = document_edits

        return edits

    def _get_enum_value_type_text_edits(
        self, old_value: str, new_value: str, definition_to_find: Definition, language_context: LanguageContext
    ) -> dict[str, TextEdit]:
        """Returns a dictionary of enum value type uri to TextEdits where the uri is the key and the list of edits is the value."""
        edits = {}
        enum_references = get_enum_references_from_context(definition_to_find, language_context)
        enum_references_to_alter = [*enum_references, definition_to_find]

        for definition in enum_references_to_alter:
            reference_lexemes = [lexeme for lexeme in definition.lexemes if remove_list_type_indicator(lexeme.value) == old_value]
            for lexeme_to_replace in reference_lexemes:
                document_edits = edits.get(lexeme_to_replace.source, [])
                replacement_range = get_location_from_lexeme(lexeme_to_replace).range
                document_edits.append(TextEdit(range=replacement_range, new_text=new_value))
                edits[str(lexeme_to_replace.source)] = document_edits

        return edits
