"""Module for the Rename Provider which handles requests to rename symbols."""

import logging
from typing import List, Optional
from pygls.server import LanguageServer
from pygls.lsp.types import Position, RenameParams, WorkspaceEdit, TextEdit, TextDocumentIdentifier
from pygls.workspace import Document
from aac.lang.constants import DEFINITION_FIELD_NAME, DEFINITION_FIELD_TYPE

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

    def handle_request(self, language_server: LanguageServer, params: RenameParams) -> Optional[WorkspaceEdit]:
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

            if symbol:
                edits = self._get_rename_edits(symbol, new_name)

                try:
                    workspace_edit = WorkspaceEdit(text_document=TextDocumentIdentifier(uri=document.uri), changes=edits)
                except Exception as error:
                    logging.error(error)

        return workspace_edit

    def _get_rename_edits(self, symbol: str, new_name: str) -> dict[str, list[TextEdit]]:
        """Returns the list of text edits based on the selected symbol's type."""

        # Strip any ':' that accompany yaml keys from the incoming replacement text
        sanitized_new_name = new_name.strip(":")
        text_to_replace = remove_list_type_indicator(symbol)

        language_context = self.language_server.language_context
        symbol_types = get_possible_symbol_types(text_to_replace, language_context)

        edits = {}
        if SymbolType.DEFINITION_NAME in symbol_types:
            definition_to_find = language_context.get_definition_by_name(text_to_replace)
            if not definition_to_find:
                logging.warn(f"Can't find references for non-definition {text_to_replace}")
            else:
                edits = self._get_definition_name_text_edits(sanitized_new_name, definition_to_find, language_context)

        if SymbolType.ENUM_VALUE_TYPE in symbol_types:
            enum_to_find = language_context.get_enum_definition_by_type(text_to_replace)
            if not enum_to_find:
                logging.warn(f"Can't find references for non-enum {text_to_replace}")
            else:
                edits = self._get_enum_value_type_text_edits(text_to_replace, sanitized_new_name, enum_to_find, language_context)

        if SymbolType.ROOT_KEY in symbol_types:
            root_fields = language_context.get_root_fields()
            key_schema_field, *_ = [field for field in root_fields if field.get(DEFINITION_FIELD_NAME) == text_to_replace]
            definition_to_find = language_context.get_definition_by_name(key_schema_field.get(DEFINITION_FIELD_TYPE))

            if not definition_to_find:
                logging.critical(f"Can't find the source definition definition '{text_to_replace}'.")
            else:
                edits = self._get_root_key_text_edits(text_to_replace, sanitized_new_name, definition_to_find, language_context)

        return edits

    def _get_definition_name_text_edits(
        self, new_name: str, definition_to_find: Definition, language_context: LanguageContext
    ) -> dict[str, list[TextEdit]]:
        """Returns a dictionary of document uri to TextEdits where the uri is the key and the list of edits the value."""
        edits: dict[str, list] = {}
        definition_references = get_definition_type_references_from_list(definition_to_find, language_context.definitions)
        definitions_to_alter = [*definition_references, definition_to_find]

        for definition in _filter_editable_definitions(definitions_to_alter):
            reference_lexemes = [
                lexeme for lexeme in definition.lexemes if remove_list_type_indicator(lexeme.value) == definition_to_find.name
            ]
            self._add_edits_from_lexemes(new_name, reference_lexemes, edits)

        return edits

    def _get_enum_value_type_text_edits(
        self, old_value: str, new_value: str, definition_to_find: Definition, language_context: LanguageContext
    ) -> dict[str, list[TextEdit]]:
        """Returns a dictionary of enum value type uri to TextEdits where the uri is the key and the list of edits is the value."""
        edits: dict[str, list] = {}
        enum_references = get_enum_references_from_context(definition_to_find, language_context)
        enum_references_to_alter = [*enum_references, definition_to_find]

        for definition in _filter_editable_definitions(enum_references_to_alter):
            reference_lexemes = [
                lexeme for lexeme in definition.lexemes if remove_list_type_indicator(lexeme.value) == old_value
            ]
            self._add_edits_from_lexemes(new_value, reference_lexemes, edits)

        return edits

    def _get_root_key_text_edits(
        self, old_value: str, new_value: str, definition_to_find: Definition, language_context: LanguageContext
    ) -> dict[str, list[TextEdit]]:
        """Returns a dictionary of uri to TextEdits where the uri is the key and the list of edits is the value."""
        edits: dict[str, list] = {}

        definitions_with_root_key = language_context.get_definitions_by_root_key(old_value)
        root_key_references = get_definition_type_references_from_list(definition_to_find, language_context.definitions)
        definitions_to_alter = [*definitions_with_root_key, *root_key_references, definition_to_find]

        for definition in _filter_editable_definitions(definitions_to_alter):
            reference_lexemes = [
                lexeme for lexeme in definition.lexemes if remove_list_type_indicator(lexeme.value) == old_value
            ]
            self._add_edits_from_lexemes(new_value, reference_lexemes, edits)

        return edits

    def _add_edits_from_lexemes(self, new_value: str, reference_lexemes: list[Lexeme], edits_list: dict[str, list]):
        """Converts lexemes to edits and adds them to the edits dictionary."""
        edits: dict = {}

        logging.error(f"Lexemes to replace {reference_lexemes}")
        for lexeme_to_replace in reference_lexemes:
            lexeme_source = str(lexeme_to_replace.source)
            replacement_range = get_location_from_lexeme(lexeme_to_replace).range
            edit = TextEdit(range=replacement_range, new_text=new_value)

            source_edits_list = edits_list.get(lexeme_source)
            if not source_edits_list:
                edits_list[lexeme_source] = [edit]
            else:
                source_edits_list.append(edit)

        return edits


def _filter_editable_definitions(definitions_to_filter: List[Definition]) -> List[Definition]:
    filtered_definitions = {definition for definition in definitions_to_filter if definition.source.is_user_editable}
    return list(filtered_definitions)
