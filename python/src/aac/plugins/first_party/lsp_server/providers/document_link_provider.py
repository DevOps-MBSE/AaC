"""Module for the Document Links Provider which handles requests for document links."""
from os import path
from pygls.server import LanguageServer
from pygls.lsp.types import DocumentLinkParams, DocumentLink
from pygls.uris import from_fs_path, to_fs_path

from aac.lang.language_context import LanguageContext
from aac.plugins.first_party.lsp_server.providers.locations import get_location_from_lexeme
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider


class DocumentLinkProvider(LspProvider):
    """Resolve the full path for AaC document references."""

    def handle_request(self, language_server: LanguageServer, params: DocumentLinkParams) -> list[DocumentLink]:
        """Return the document links for a given file."""
        self.language_server = language_server
        file_path = to_fs_path(params.text_document.uri)
        return self.get_document_links(file_path)

    def get_document_links(self, document_uri: str) -> list[DocumentLink]:
        """
        Return a list of DocumentLinks based on the content in the file.

        Args:
            document (str): The document's file path.

        Returns:
            A list of DocumentLinks linking the file to the item at the current position. If there is nothing
            found at the current position, an empty list is returned.
        """
        language_context: LanguageContext = self.language_server.language_context
        links: list[DocumentLink] = []

        for definition in language_context.get_definitions_by_file_uri(document_uri):
            imports = definition.get_imports()

            for import_path in imports:
                absolute_import_path = import_path
                if not path.isabs(import_path):
                    source_directory = path.dirname(definition.source.uri)
                    absolute_import_path = path.normpath(path.join(source_directory, import_path))
                    absolute_import_path = path.abspath(absolute_import_path)

                target_uri = from_fs_path(absolute_import_path)
                file_name = path.basename(absolute_import_path)
                tooltip = f"Go to {absolute_import_path}"
                link_lexeme = [lexeme for lexeme in definition.lexemes if file_name in lexeme.value or file_name == lexeme.value][0]
                link_location = get_location_from_lexeme(link_lexeme)
                links.append(DocumentLink(range=link_location.range, target=target_uri, tooltip=tooltip))

        return links
