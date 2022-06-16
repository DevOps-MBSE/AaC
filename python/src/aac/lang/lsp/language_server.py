"""The Architecture-as-Code Language Server."""

import os
from attr import Factory, attrib, attrs, validators
import difflib
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
        workspace_files (dict[str, ManagedWorkspaceFile]): The files present in the workspace containing definitions.
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
        server: LanguageServer = self.language_server
        server.sync_kind = TextDocumentSyncKind.FULL

        @server.feature(methods.TEXT_DOCUMENT_DID_OPEN)
        async def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
            """Text document did open notification."""
            logging.info(f"Text document opened by LSP client {params.text_document.uri}.")

            file_uri = params.text_document.uri
            managed_file = self.workspace_files.get(file_uri)

            if not managed_file:
                managed_file = ManagedWorkspaceFile(file_uri)
                self.workspace_files[file_uri] = managed_file

            managed_file.is_client_managed = True
            _, file_path = file_uri.split("file://")
            self.language_context.add_definitions_to_context(parse(params.text_document.text, file_path))

        @server.feature(methods.TEXT_DOCUMENT_DID_CLOSE)
        async def did_close(ls: LanguageServer, params: DidCloseTextDocumentParams):
            """Text document did close notification."""
            logging.info(f"Text document closed by LSP client {params.text_document.uri}.")

            file_uri = params.text_document.uri
            managed_file = self.workspace_files.get(file_uri)
            managed_file.is_client_managed = False

        @server.feature(methods.TEXT_DOCUMENT_DID_CHANGE)
        async def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams):
            """Text document did change notification."""
            logging.info(f"Text document altered by LSP client {params.text_document.uri}.")

            file_content = params.content_changes[0].text
            altered_definitions = parse(file_content)

            for altered_definition in altered_definitions:
                # At the moment we have to rely on definition names, but we'll need to update definitions based on file URI
                old_definition = self.language_context.get_definition_by_name(altered_definition.name)

                if old_definition:
                    old_definition_lines = old_definition.to_yaml().split(os.linesep)
                    altered_definition_lines = altered_definition.to_yaml().split(os.linesep)
                    changes = "\n".join(list(difflib.ndiff(old_definition_lines, altered_definition_lines))).strip()
                    logging.info(f"Updating definition: {old_definition.name}.\n Differences:\n{changes}")
                else:
                    logging.info(f"Adding definition: {altered_definition.name}.")
                    self.language_context.add_definition_to_context(altered_definition)

            self.language_context.update_definitions_in_context(altered_definitions)

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
