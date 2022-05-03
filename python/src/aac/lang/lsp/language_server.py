"""The Architecture-as-Code Language Server."""

from attr import Factory, attrib, attrs, validators
import logging
from typing import Optional
from pygls.server import LanguageServer
from pygls.lsp import (
    CompletionOptions,
    CompletionParams,
    Hover,
    HoverParams,
    TextDocumentSyncKind,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    methods
)

from aac.parser import parse
from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.language_context import LanguageContext
from aac.lang.lsp.managed_workspace_file import ManagedWorkspaceFile
from aac.lang.lsp.code_completion_provider import CodeCompletionProvider


@attrs
class AacLanguageServer:
    """Manages the various aspects of the AaC Language Server -- including AaC specific functionality.

    Attributes:
        language_server (LanguageServer): The underlying pygls language server
        language_context (LanguageContext): The AaC LanguageContext for the language server
        code_completion_provider (CodeCompletionProvider): The provider for Code Completion Language Server features
    """

    language_server: Optional[LanguageServer] = attrib(default=None, validator=validators.instance_of((type(None), LanguageServer)))
    language_context: Optional[LanguageContext] = attrib(default=None, validator=validators.instance_of((type(None), LanguageContext)))
    code_completion_provider: Optional[CodeCompletionProvider] = attrib(default=None, validator=validators.instance_of((type(None), CodeCompletionProvider)))
    workspace_files: dict[str, ManagedWorkspaceFile] = attrib(default=Factory(dict), validator=validators.instance_of(dict))

    def __attrs_post_init__(self):
        """Post init hook for attrs classes."""
        self.configure_lsp()

    def configure_lsp(self):
        """Configure and setup the LSP server so that it's ready to execute."""
        self.language_context = get_initialized_language_context()
        self.language_server = self.language_server or LanguageServer()
        self.code_completion_provider = self.code_completion_provider or CodeCompletionProvider()
        self.setup_features()

    def setup_features(self) -> None:
        """Configure the server with the supported features."""
        server = self.language_server
        server.sync_kind = TextDocumentSyncKind.FULL

        @server.feature(methods.TEXT_DOCUMENT_DID_OPEN)
        async def did_open(ls, params: DidOpenTextDocumentParams):
            """Text document did open notification."""
            file_uri = params.text_document.uri
            managed_file = self.workspace_files.get(file_uri)

            if not managed_file:
                managed_file = ManagedWorkspaceFile(file_uri)
                self.workspace_files[file_uri] = managed_file

            managed_file.is_client_managed = True
            _, file_path = file_uri.split("file://")
            self.language_context.add_definitions_to_context(parse(file_path))
            logging.info(f"Text document opened by LSP client {file_uri}.")

        @server.feature(methods.TEXT_DOCUMENT_DID_CLOSE)
        def did_close(server: LanguageServer, params: DidCloseTextDocumentParams):
            """Text document did close notification."""
            file_uri = params.text_document.uri
            managed_file = self.workspace_files.get(file_uri)
            managed_file.is_client_managed = False
            logging.info(f"Text document closed by LSP client {file_uri}.")

        @server.feature(methods.TEXT_DOCUMENT_DID_CHANGE)
        def did_change(ls, params: DidChangeTextDocumentParams):
            """Text document did change notification."""
            file_uri = params.text_document.uri
            _, file_path = file_uri.split("file://")
            affected_definitions = self.language_context.get_definitions_by_file_uri(file_path)
            altered_definition_names = [definition.name for definition in affected_definitions]
            logging.info(f"Definitions identified to update due to doc change: {altered_definition_names}")

            logging.info(f"Text document altered by LSP client {params.text_document.uri}.")

        @server.feature(methods.HOVER)
        async def handle_hover(ls: LanguageServer, params: HoverParams):
            """Handle a hover request."""
            return Hover(contents="Hello from your friendly AaC LSP server!")

        trigger_and_commit_chars = self.code_completion_provider.get_trigger_characters()

        @server.feature(methods.COMPLETION, CompletionOptions(trigger_characters=trigger_and_commit_chars))
        async def handle_completion(ls: LanguageServer, params: CompletionParams):
            """Handle a completion request."""
            completion_results = self.code_completion_provider.handle_code_completion(ls, params)
            logging.debug(f"Completion results: {completion_results}")
            return completion_results
