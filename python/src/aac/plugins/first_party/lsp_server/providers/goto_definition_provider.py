"""Module for the Goto Definition Provider which handles all goto definition requests."""
import logging
from pygls.lsp import Location, Position, DefinitionParams
from pygls.server import LanguageServer
from pygls.workspace import Document
from aac.lang.definitions.definition import Definition

from aac.lang.definitions.type import remove_list_type_indicator
from aac.lang.language_context import LanguageContext
from aac.plugins.first_party.lsp_server.providers.symbols import get_symbol_at_position, get_possible_symbol_types, SymbolType
from aac.plugins.first_party.lsp_server.providers.locations import get_location_from_lexeme
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider
from aac.lang.definitions.lexeme import Lexeme


class GotoDefinitionProvider(LspProvider):
    """Resolve the location where a specified name is defined."""
    language_server: LanguageServer

    def handle_request(self, language_server: LanguageServer, params: DefinitionParams) -> list[Location]:
        """Return the location at which the specified item is found."""
        self.language_server = language_server
        return self.get_definition_location_at_position(self.language_server.workspace.documents, params.text_document.uri, params.position)

    def get_definition_location_at_position(self, documents: dict[str, Document], current_uri: str, position: Position) -> list[Location]:
        """
        Return the location(s) where the AaC reference at the specified position is defined.

        Args:
            documents (dict[str, Document]): A container mapping document names to the associated LSP document.
            current_uri (str): The URI of the file that's currently active.
            position (Position): The position of the cursor in `current_uri` whose definition is being searched.

        Returns:
            A list of Locations at which the item at `position` is defined. If there is nothing
            found at the specified position, an empty list is returned.
        """
        document = documents.get(current_uri)
        locations = []
        if document:
            symbol = get_symbol_at_position(document.source, position.line, position.character)
            locations = self.get_definition_location(symbol) if symbol else []

        return locations

    def get_definition_location(self, name: str) -> list[Location]:
        """
        Return the location(s) where the AaC reference is defined.

        Args:
            documents (dict[str, Document]): The documents in the workspace in which to search for name.
            name (str): The name of the item whose location is being determined.

        Returns:
            A list of Locations at which the `name`d item is defined. If there is no named item, an
            empty list is returned.
        """
        if not name:
            return []

        language_context: LanguageContext = self.language_server.language_context

        locations = []
        name = remove_list_type_indicator(name).strip(":")
        symbol_types = get_possible_symbol_types(name, language_context)

        if SymbolType.DEFINITION_NAME in symbol_types:
            definition_to_find = language_context.get_definition_by_name(name)
            if not definition_to_find:
                logging.warn(f"Can't find references for non-definition {name}")
            else:
                locations.extend(self.get_definition_name_lexeme_location(definition_to_find))

        if SymbolType.ENUM_VALUE_TYPE in symbol_types:
            definition_to_find = language_context.get_enum_definition_by_type(name)
            if definition_to_find:
                locations.extend(self.get_enum_value_lexeme_location(definition_to_find, name))

        if SymbolType.ROOT_KEY_NAME in symbol_types:
            definition_to_find = language_context.get_root_keys_definition()
            if definition_to_find:
                locations.extend(self.get_root_key_definition_lexeme_location(definition_to_find, name))

        return locations

    def get_definition_name_lexeme_location(self, definition: Definition) -> list[Location]:
        """
        Returns a list of locations corresponding to the name declaration in definition structures.

        Args:
            definition (Definition): The definition to pull the name lexeme from.


        Returns:
            A list, probably consisting of only one element, of locations corresponding to lexemes of definition names
        """
        def filter_lexeme_by_reference_name(lexeme: Lexeme) -> bool:
            return lexeme.value == definition.name

        locations = []
        referencing_lexemes = filter(filter_lexeme_by_reference_name, definition.lexemes)
        for lexeme in referencing_lexemes:
            previous_lexeme = definition.lexemes[definition.lexemes.index(lexeme) - 1]
            if "name" in previous_lexeme.value:
                locations.append(get_location_from_lexeme(lexeme))

        return locations

    def get_enum_value_lexeme_location(self, definition: Definition, enum_value: str) -> list[Location]:
        """
        Returns a list of locations corresponding to the enum value declaration in the enum definition's structure.

        Args:
            definition (Definition): The definition to pull the enum value lexeme from.
            enum_value (str): The string value to target.


        Returns:
            A list, probably consisting of only one element, of locations corresponding to lexemes of definition names
        """
        def filter_lexeme_by_reference_name(lexeme: Lexeme) -> bool:
            return lexeme.value == enum_value

        def filter_for_value_lexeme(lexeme: Lexeme) -> bool:
            return lexeme.value == "values"

        locations = []
        referencing_lexemes = filter(filter_lexeme_by_reference_name, definition.lexemes)
        values_lexeme = list(filter(filter_for_value_lexeme, definition.lexemes))[0]
        values_lexeme_index = definition.lexemes.index(values_lexeme)

        for lexeme in referencing_lexemes:
            if values_lexeme_index < definition.lexemes.index(lexeme):
                locations.append(get_location_from_lexeme(lexeme))

        return locations

    def get_root_key_definition_lexeme_location(self, definition: Definition, root_key: str) -> list[Location]:
        """
        Returns a list of locations corresponding to the root key string's declaration in the root keys definition's structure.

        Args:
            definition (Definition): The definition to pull the enum value lexeme from.
            root_key (str): The string value to target.


        Returns:
            A list, probably consisting of only one element, of locations corresponding to lexemes of definition names
        """
        def filter_lexeme_by_reference_name(lexeme: Lexeme) -> bool:
            return lexeme.value == root_key

        locations = []
        referencing_lexemes = filter(filter_lexeme_by_reference_name, definition.lexemes)
        for lexeme in referencing_lexemes:
            lexeme_index = definition.lexemes.index(lexeme)
            previous_lexeme = definition.lexemes[lexeme_index - 1]
            if "name" in previous_lexeme.value and lexeme_index > 0:
                locations.append(get_location_from_lexeme(lexeme))

        return locations
