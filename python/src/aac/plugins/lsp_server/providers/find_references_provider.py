"""Module for the Find All References Provider which handles requests to find all references."""

import logging
from pygls.server import LanguageServer
from pygls.lsp.types.basic_structures import Location, Position, Range
from pygls.lsp.types.language_features.references import ReferenceParams
from pygls.workspace import Document

from aac.lang.definitions.references import get_definition_type_references_from_list
from aac.lang.definitions.type import remove_list_type_indicator
from aac.lang.definitions.lexeme import Lexeme
from aac.plugins.lsp_server.providers.common import get_symbol_at_position
import aac.plugins.lsp_server.providers.lsp_provider as lsp_provider


class FindReferencesProvider(lsp_provider.LspProvider):
    """Resolve the reference locations for a definition name or root key."""

    def handle_request(self, ls: LanguageServer, params: ReferenceParams) -> list[Location]:
        """Return the locations at which references to the item are found."""
        self.language_server = ls
        return self.get_reference_locations(self.language_server.workspace.documents, params.text_document.uri, params.position)

    def get_reference_locations(self, documents: dict[str, Document], current_uri: str, position: Position) -> list[Location]:
        """
        Return the location(s) where the AaC definition is referenced at.

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
            offset = document.offset_at_position(position)
            locations = self.get_definition_location_of_name(documents, get_symbol_at_position(document.source, offset))

        return locations

    def get_definition_location_of_name(self, documents: dict[str, Document], name: str) -> list[Location]:
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

        lsp_context = self.language_server.language_context

        locations = []
        name = remove_list_type_indicator(name).strip(":")
        definition_to_find = lsp_context.get_definition_by_name(name)

        if not definition_to_find:
            logging.warn(f"Can't find references for non-definition {name}")
        else:
            referencing_definitions = get_definition_type_references_from_list(definition_to_find, lsp_context.definitions)

            for definition in referencing_definitions:
                def filter_lexeme_by_reference_name(lexeme: Lexeme) -> bool:
                    return remove_list_type_indicator(lexeme.value) == name

                referencing_lexemes = filter(filter_lexeme_by_reference_name, definition.lexemes)

                for lexeme in referencing_lexemes:
                    start_position = Position(line=lexeme.location.line, character=lexeme.location.column)
                    end_position = Position(line=lexeme.location.line, character=lexeme.location.column + lexeme.location.span)
                    locations.append(Location(uri=lexeme.source, range=Range(start=start_position, end=end_position)))

        return locations

    def get_ranges_containing_name(self, content: str, name: str) -> list[Range]:
        """
        Return the cursor position of the item in content.

        Args:
            content (str): The content from the workspace document in which to find the named item.
            name (str): The item to search for in the document's content.

        Returns:
            A list of Ranges where in the content
        """

        def get_end_position(position: Position) -> Position:
            end_position = position.copy()
            end_position.character += len(name)
            return end_position

        lines = content.splitlines()
        starting_positions = [Position(line=i, character=lines[i].find(name)) for i, line in enumerate(lines) if name in line]
        return [Range(start=start_pos, end=get_end_position(start_pos)) for start_pos in starting_positions]

    def _is_definition(self, name: str, lines: list[str]) -> bool:
        """
        Returns a boolean indicating if the named item at the specified location is a definition.

        Args:
            name (str): The named item to check.
            lines (list[str]): The lines up to the one to be searched for the named item.

        Returns:
            A boolean value indicating that the named item is defined in the provided content.
        """

        def is_schema_definition() -> bool:
            return context.is_definition_type(name) and f"name: {name}" == lines[0]

        def is_enum_definition() -> bool:
            return context.get_enum_definition_by_type(name) is not None and f"- {name}" == lines[0]

        lines.reverse()
        lines = [line.strip() for line in lines]
        context = self.language_server.language_context
        return is_schema_definition() or is_enum_definition()
