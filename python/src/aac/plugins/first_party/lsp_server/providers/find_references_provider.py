"""Module for the Find All References Provider which handles requests to find all references."""

import logging
from pygls.server import LanguageServer
from pygls.lsp.types import Location, Position, ReferenceParams
from pygls.workspace import Document

from aac.lang.definitions.definition import Definition
from aac.lang.language_context import LanguageContext
from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.references import get_definition_type_references_from_list
from aac.lang.definitions.type import remove_list_type_indicator
from aac.lang.definitions.lexeme import Lexeme
from aac.plugins.first_party.lsp_server.providers.symbols import get_symbol_at_position, SymbolType, get_possible_symbol_types
from aac.plugins.first_party.lsp_server.providers.locations import get_location_from_lexeme
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider


class FindReferencesProvider(LspProvider):
    """Resolve the reference locations for a definition name or root key."""

    def handle_request(self, language_server: LanguageServer, params: ReferenceParams) -> list[Location]:
        """Return the locations at which references to the item are found."""
        self.language_server = language_server
        return self.get_reference_locations(
            self.language_server.workspace.documents, params.text_document.uri, params.position
        )

    def get_reference_locations(self, documents: dict[str, Document], current_uri: str, position: Position) -> list[Location]:
        """
        Return the location(s) where the AaC definition is referenced at.

        Args:
            documents (dict[str, Document]): A container mapping document names to the associated LSP document.
            current_uri (str): The URI of the file that's currently active.
            position (Position): The position of the cursor in `current_uri` whose definition is being searched.

        Returns:
            A list of Locations at which the item at `position` is referenced. If there is nothing
            found at the specified position, an empty list is returned.
        """
        document = documents.get(current_uri)
        locations = []
        if document:
            symbol = get_symbol_at_position(document.source, position.line, position.character)
            locations = self.get_symbol_reference_locations(symbol) if symbol else []

        return locations

    def get_symbol_reference_locations(self, symbol: str) -> list[Location]:
        """
        Return the location(s) where the target value is referenced.

        Args:
            symbol (str): The symbol whose location is being determined.

        Returns:
            A list of Locations at which the `symbol` is referenced. If no symbol is found, an
            empty list is returned.
        """
        if not symbol:
            return []

        language_context = self.language_server.language_context

        locations = []
        name = remove_list_type_indicator(symbol).strip(":")
        symbol_types = get_possible_symbol_types(name, language_context)

        if SymbolType.DEFINITION_NAME in symbol_types:
            definition_to_find = language_context.get_definition_by_name(name)
            if not definition_to_find:
                logging.warn(f"Can't find references for non-definition {name}")
            else:
                locations.extend(self.get_definition_name_reference_locations(definition_to_find, language_context))

        if SymbolType.ROOT_KEY_NAME in symbol_types:
            locations.extend(self.get_root_key_reference_locations(name, language_context))

        return locations

    def get_definition_name_reference_locations(
        self, definition_to_find: Definition, language_context: LanguageContext
    ) -> list[Location]:
        """
        Returns a list of locations corresponding to the name declaration in definition structures.

        Args:
            definition_to_find (Definition): The definition to pull the name lexeme from.
            language_context (LanguageContext): The LanguageContext in which to look for the definition.

        Returns:
            A list, probably consisting of only one element, of locations corresponding to lexemes of definition names
        """
        locations = []
        referencing_definitions = get_definition_type_references_from_list(definition_to_find, language_context.definitions)

        for definition in referencing_definitions:

            def filter_lexeme_by_reference_name(lexeme: Lexeme) -> bool:
                return remove_list_type_indicator(lexeme.value) == definition_to_find.name

            referencing_lexemes = filter(filter_lexeme_by_reference_name, definition.lexemes)
            for lexeme in referencing_lexemes:
                locations.append(get_location_from_lexeme(lexeme))

        return locations

    def get_root_key_reference_locations(self, root_key: str, language_context: LanguageContext) -> list[Location]:
        """
        Returns a list of locations corresponding to the name declaration in definition structures.

        Args:
            root_key (str): The root key for which locations of references will be returned.
            language_context (LanguageContext): The LanguageContext in which to look for the root key.

        Returns:
            A list, probably consisting of only one element, of locations corresponding to lexemes of definition names
        """
        locations = []
        referencing_definitions = get_definitions_by_root_key(root_key, language_context.definitions)

        for definition in referencing_definitions:
            locations.append(get_location_from_lexeme(definition.lexemes[0]))

        return locations
