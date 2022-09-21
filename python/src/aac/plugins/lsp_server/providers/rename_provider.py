"""Module for the Rename Provider which handles requests to rename symbols."""

import logging
from typing import Optional
from pygls.server import LanguageServer
from pygls.lsp.types import Range, Position, RenameParams, WorkspaceEdit, TextEdit, TextDocumentIdentifier
from pygls.workspace import Document

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.references import get_definition_type_references_from_list
from aac.lang.definitions.type import remove_list_type_indicator
from aac.lang.definitions.lexeme import Lexeme
from aac.plugins.lsp_server.providers.symbols import (
    get_symbol_at_position,
    get_symbol_range_at_position,
    get_possible_symbol_types,
    SymbolType,
)
from aac.plugins.lsp_server.providers.locations import get_location_from_lexeme
import aac.plugins.lsp_server.providers.lsp_provider as lsp_provider


class RenameProvider(lsp_provider.LspProvider):
    """Handles the rename requests."""

    def handle_request(self, ls: LanguageServer, params: RenameParams) -> WorkspaceEdit:
        """Return the locations at which references to the item are found."""
        self.language_server = ls
        return self.get_rename_edits(
            self.language_server.workspace.documents, params.text_document.uri, params.position, params.new_name
        )

    def get_rename_edits(
        self, documents: dict[str, Document], current_uri: str, position: Position, new_name: str
    ) -> Optional[WorkspaceEdit]:
        """
        Return the rename edits where the AaC's.

        Args:
            documents (dict[str, Document]): A container mapping document names to the associated LSP document.
            current_uri (str): The URI of the file that's currently active.
            position (Position): The position of the cursor in `current_uri` whose definition is being searched.
            new_name (str): The new name to replace instances of the selected symbol with.

        Returns:
            A list of Locations at which the item at `position` is referenced. If there is nothing
            found at the specified position, an empty list is returned.
        """
        document = documents.get(current_uri)
        workspace_edit = None

        if document:
            symbol = get_symbol_at_position(document.source, position.line, position.character)

            if symbol:
                edits = self._get_rename_edits(symbol, new_name) if symbol else {}
                select_symbol_text_edit = TextEdit(
                    range=self._get_symbol_rename_edit(document.source, position, new_name), new_text=new_name
                )
                edits.get(current_uri, []).append(select_symbol_text_edit)

                try:
                    workspace_edit = WorkspaceEdit(text_document=TextDocumentIdentifier(uri=document.uri), changes=edits)
                except Exception as error:
                    logging.error(error)

        return workspace_edit

    def _get_rename_edits(self, symbol: str, new_name: str) -> dict[str, TextEdit]:
        """
        Return the location(s) where the target value is referenced.

        Args:
            symbol (str): The symbol whose location is being determined.

        Returns:
            A list of Locations at which the `symbol` is referenced. If no symbol is found, an
            empty list is returned.
        """
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
                edits = self.get_definition_name_reference_locations(new_name, definition_to_find, language_context)

        return edits

    def _get_symbol_rename_edit(self, source: str, position: Position, new_name: str) -> Range:
        """Returns a TextEdit for the initially-selected symbol."""
        symbol_range = get_symbol_range_at_position(source, position.line, position.character)
        # _update_range_to_renamed_content_length(symbol_range, new_name)
        return symbol_range

    def get_definition_name_reference_locations(
        self, new_name: str, definition_to_find: Definition, language_context: LanguageContext
    ) -> dict[str, TextEdit]:
        """
        Returns a list of locations corresponding to the name declaration in definition structures.

        Args:
            new_name (str):
            definition_to_find (Definition): The definition to pull the name lexeme from.
            language_context (LanguageContext): The LanguageContext in which to look for the definition.

        Returns:
            A dictionary of document uri to TextEdits where the uri is the key and the list of edits the value.
        """
        edits = {}
        referencing_definitions = get_definition_type_references_from_list(definition_to_find, language_context.definitions)

        for definition in referencing_definitions:

            def filter_lexeme_by_reference_name(lexeme: Lexeme) -> bool:
                return remove_list_type_indicator(lexeme.value) == definition_to_find.name

            referencing_lexemes = filter(filter_lexeme_by_reference_name, definition.lexemes)

            for lexeme_to_replace in referencing_lexemes:
                document_edits = edits.get(lexeme_to_replace.source, [])
                document_edits.append(_lexeme_to_text_edit(lexeme_to_replace, new_name))
                edits[str(lexeme_to_replace.source)] = document_edits

        return edits


def _lexeme_to_text_edit(lexeme: Lexeme, new_value: str) -> TextEdit:
    """Returns a TextEdit based on the location of the lexeme, but with the length and value of the new value."""
    replacing_range = get_location_from_lexeme(lexeme).range
    return TextEdit(range=replacing_range, new_text=new_value)


def _update_range_to_renamed_content_length(range_to_update: Range, new_value: str) -> None:
    """Alters the Range value passed in as an argument to be the length of the new value."""
    range_to_update.end.character = range_to_update.start.character + len(new_value)
