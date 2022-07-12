"""The Architecture-as-Code Language Server."""

import os
import difflib
import logging
from typing import Optional
from pygls.lsp.types.language_features.definition import DefinitionParams
from pygls.protocol import LanguageServerProtocol
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
from aac.lang.definitions.structure import strip_undefined_fields_from_definition
from aac.lang.language_context import LanguageContext
from aac.lang.lsp.managed_workspace_file import ManagedWorkspaceFile
from aac.lang.lsp.providers.lsp_provider import LspProvider
from aac.lang.lsp.providers.code_completion_provider import CodeCompletionProvider
from aac.lang.lsp.providers.goto_definition_provider import GotoDefinitionProvider


class AacLanguageServer(LanguageServer):
    """Manages the various aspects of the AaC Language Server -- including AaC specific functionality.

    Attributes:
        language_context (LanguageContext): The AaC LanguageContext for the language server.
        providers (dict[str, list[LspProvider]]): The providers for handling non-trivial Language Server features.
        workspace_files (dict[str, ManagedWorkspaceFile]): The files present in the workspace containing definitions.
    """

    language_context: Optional[LanguageContext]
    providers: dict[str, LspProvider]
    workspace_files: dict[str, ManagedWorkspaceFile]

    def __init__(self, language_context=None, providers={}, workspace_files={}, loop=None, protocol_cls=LanguageServerProtocol, max_workers: int = 2):
        """Docstring."""
        super().__init__(loop, protocol_cls, max_workers)

        self.language_context = language_context
        self.providers = providers
        self.workspace_files = workspace_files

        self.configure_lsp()

    def configure_lsp(self):
        """Configure and setup the LSP server so that it's ready to execute."""
        self.language_context = get_initialized_language_context()
        self.configure_providers()
        self.setup_features()

    def configure_providers(self):
        """Configure and setup the providers that make LSP functionality available for the AaC LSP server."""
        self.providers[methods.COMPLETION] = self.providers.get(methods.COMPLETION, CodeCompletionProvider())
        self.providers[methods.DEFINITION] = self.providers.get(methods.DEFINITION, GotoDefinitionProvider())

    def setup_features(self) -> None:
        """Configure the server with the supported features."""
        self.sync_kind = TextDocumentSyncKind.FULL

        self.feature(methods.TEXT_DOCUMENT_DID_OPEN)(did_open)
        self.feature(methods.TEXT_DOCUMENT_DID_CLOSE)(did_close)
        self.feature(methods.TEXT_DOCUMENT_DID_CHANGE)(did_change)

        trigger_and_commit_chars = self.providers.get(methods.COMPLETION).get_trigger_characters()
        completion_options = CompletionOptions(trigger_characters=trigger_and_commit_chars)
        self.feature(methods.COMPLETION, completion_options)(handle_completion)
        self.feature(methods.HOVER)(handle_hover)
        self.feature(methods.DEFINITION)(handle_goto_definition)


async def did_open(ls: AacLanguageServer, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    logging.info(f"Text document opened by LSP client {params.text_document.uri}.")

    file_uri = params.text_document.uri
    managed_file = ls.workspace_files.get(file_uri)

    if not managed_file:
        managed_file = ManagedWorkspaceFile(file_uri)
        ls.workspace_files[file_uri] = managed_file

    managed_file.is_client_managed = True
    _, file_path = file_uri.split("file://")
    ls.language_context.add_definitions_to_context(parse(params.text_document.text, file_path))


async def did_close(ls: AacLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    logging.info(f"Text document closed by LSP client {params.text_document.uri}.")

    file_uri = params.text_document.uri
    managed_file = ls.workspace_files.get(file_uri)
    managed_file.is_client_managed = False


async def did_change(ls: AacLanguageServer, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    document_uri = params.text_document.uri
    logging.info(f"Text document altered by LSP client {document_uri}.")

    file_content = params.content_changes[0].text
    incoming_definitions = parse(file_content)
    new_definitions = []
    altered_definitions = []

    for incoming_definition in incoming_definitions:
        sanitized_definition = strip_undefined_fields_from_definition(incoming_definition, ls.language_context)
        # At the moment we have to rely on definition names, but we'll need to update definitions based on file URI
        old_definition = ls.language_context.get_definition_by_name(sanitized_definition.name)

        if old_definition:
            altered_definitions.append(sanitized_definition)

            old_definition_lines = old_definition.to_yaml().split(os.linesep)
            altered_definition_lines = incoming_definition.to_yaml().split(os.linesep)
            changes = "\n".join(list(difflib.ndiff(old_definition_lines, altered_definition_lines))).strip()
            logging.info(f"Updating definition: {old_definition.name}.\n Differences:\n{changes}")
        else:
            logging.info(f"Adding definition: {sanitized_definition.name}.")
            new_definitions.append(sanitized_definition)

    ls.language_context.add_definitions_to_context(new_definitions)
    ls.language_context.update_definitions_in_context(altered_definitions)


async def handle_completion(ls: AacLanguageServer, params: CompletionParams):
    """Handle a completion request."""
    code_completion_provider = ls.providers.get(methods.COMPLETION)
    completion_results = code_completion_provider.handle_request(ls, params)
    logging.debug(f"Completion results: {completion_results}")
    return completion_results


async def handle_hover(ls: AacLanguageServer, params: HoverParams):
    """Handle a hover request."""
    return Hover(contents="Hello from your friendly AaC LSP server!")


async def handle_goto_definition(ls: AacLanguageServer, params: DefinitionParams):
    """Handle a goto definition request."""
    goto_definition_provider = ls.providers.get(methods.DEFINITION)
    goto_definition_results = goto_definition_provider.handle_request(ls, params)
    logging.debug(f"Goto Definition results: {goto_definition_results}")
    return goto_definition_results
