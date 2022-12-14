"""The Architecture-as-Code Language Server."""
import difflib
import logging

from asyncio import ensure_future
from os import linesep
from typing import Optional

from pygls.lsp import (
    CompletionOptions,
    CompletionParams,
    DefinitionParams,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    HoverParams,
    PublishDiagnosticsParams,
    ReferenceParams,
    RenameParams,
    SemanticTokensParams,
    TextDocumentSyncKind,
    methods,
)
from pygls.protocol import LanguageServerProtocol
from pygls.server import LanguageServer
from pygls.uris import to_fs_path

from aac import __version__ as AAC_VERSION
from aac.io.parser import parse
from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.language_context import LanguageContext
from aac.plugins.first_party.lsp_server.managed_workspace_file import ManagedWorkspaceFile
from aac.plugins.first_party.lsp_server.providers.code_completion_provider import CodeCompletionProvider
from aac.plugins.first_party.lsp_server.providers.find_references_provider import FindReferencesProvider
from aac.plugins.first_party.lsp_server.providers.goto_definition_provider import GotoDefinitionProvider
from aac.plugins.first_party.lsp_server.providers.hover_provider import HoverProvider
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider
from aac.plugins.first_party.lsp_server.providers.prepare_rename_provider import PrepareRenameProvider
from aac.plugins.first_party.lsp_server.providers.publish_diagnostics_provider import PublishDiagnosticsProvider
from aac.plugins.first_party.lsp_server.providers.rename_provider import RenameProvider
from aac.plugins.first_party.lsp_server.providers.semantic_tokens_provider import SemanticTokensProvider


LANGUAGE_SERVER_NAME = "AaCLanguageServer"
LANGUAGE_SERVER_VERSION = AAC_VERSION


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

    def __init__(
        self,
        language_context=None,
        providers={},
        workspace_files={},
        loop=None,
        protocol_cls=LanguageServerProtocol,
        max_workers: int = 2,
    ):
        """Create an AaC Language Server."""
        super().__init__(LANGUAGE_SERVER_NAME, LANGUAGE_SERVER_VERSION, loop, protocol_cls, max_workers)

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
        self.providers[methods.REFERENCES] = self.providers.get(methods.REFERENCES, FindReferencesProvider())
        self.providers[methods.HOVER] = self.providers.get(methods.HOVER, HoverProvider())
        self.providers[methods.RENAME] = self.providers.get(methods.RENAME, RenameProvider())
        self.providers[methods.PREPARE_RENAME] = self.providers.get(methods.PREPARE_RENAME, PrepareRenameProvider())
        self.providers[methods.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL] = self.providers.get(
            methods.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, SemanticTokensProvider()
        )
        self.providers[methods.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS] = self.providers.get(
            methods.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS, PublishDiagnosticsProvider()
        )

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
        self.feature(methods.REFERENCES)(handle_references)
        self.feature(methods.RENAME)(handle_rename)
        self.feature(methods.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)(handle_publish_diagnostics)
        self.feature(methods.PREPARE_RENAME)(handle_prepare_rename)

        semantic_tokens_legend = self.providers.get(methods.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL).get_semantic_tokens_legend()
        self.feature(methods.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, semantic_tokens_legend)(handle_semantic_tokens)


async def did_open(ls: AacLanguageServer, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    logging.info(f"Text document opened by LSP client {params.text_document.uri}.")

    file_uri = params.text_document.uri
    managed_file = ls.workspace_files.get(file_uri)

    if not managed_file:
        managed_file = ManagedWorkspaceFile(file_uri)
        ls.workspace_files[file_uri] = managed_file

    managed_file.is_client_managed = True
    file_path = to_fs_path(file_uri)
    ls.language_context.add_definitions_to_context(parse(file_path))

    ensure_future(handle_publish_diagnostics(ls, PublishDiagnosticsParams(uri=params.text_document.uri, diagnostics=[])))


async def did_close(ls: AacLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    logging.info(f"Text document closed by LSP client {params.text_document.uri}.")

    file_uri = params.text_document.uri
    managed_file = ls.workspace_files.get(file_uri)
    managed_file.is_client_managed = False


async def did_change(ls: AacLanguageServer, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    document_path = to_fs_path(params.text_document.uri)
    logging.info(f"Text document altered by LSP client {document_path}.")

    ensure_future(handle_publish_diagnostics(ls, PublishDiagnosticsParams(uri=params.text_document.uri, diagnostics=[])))

    file_content = params.content_changes[0].text
    incoming_definitions_dict = {definition.name: definition for definition in parse(file_content, document_path)}
    new_definitions = []
    altered_definitions = []

    old_definitions = ls.language_context.get_definitions_by_file_uri(document_path)
    old_definitions_to_update_dict = {
        definition.name: definition for definition in old_definitions if definition.name in incoming_definitions_dict
    }
    old_definitions_to_delete = [
        definition for definition in old_definitions if definition.name not in incoming_definitions_dict
    ]

    for incoming_definition_name, incoming_definition in incoming_definitions_dict.items():
        old_definition = old_definitions_to_update_dict.get(incoming_definition_name)

        if old_definition:
            incoming_definition.uid = old_definition.uid
            altered_definitions.append(incoming_definition)

            old_definition_lines = old_definition.to_yaml().split(linesep)
            altered_definition_lines = incoming_definition.to_yaml().split(linesep)
            changes = linesep.join(list(difflib.ndiff(old_definition_lines, altered_definition_lines))).strip()
            logging.info(f"Updating definition: {old_definition.name}.\n Differences:\n{changes}")
        else:
            logging.info(f"Adding definition: {incoming_definition.name}.")
            new_definitions.append(incoming_definition)

    ls.language_context.add_definitions_to_context(new_definitions)
    ls.language_context.update_definitions_in_context(altered_definitions)
    ls.language_context.remove_definitions_from_context(old_definitions_to_delete)


async def handle_completion(ls: AacLanguageServer, params: CompletionParams):
    """Handle the completion request."""
    code_completion_provider = ls.providers.get(methods.COMPLETION)
    completion_results = code_completion_provider.handle_request(ls, params)
    logging.debug(f"Completion results: {completion_results}")
    return completion_results


async def handle_hover(ls: AacLanguageServer, params: HoverParams):
    """Handle the hover request."""
    hover_provider = ls.providers.get(methods.HOVER)
    hover_results = hover_provider.handle_request(ls, params)
    logging.debug(f"Hover results: {hover_results}")
    return hover_results


async def handle_goto_definition(ls: AacLanguageServer, params: DefinitionParams):
    """Handle the goto definition request."""
    goto_definition_provider = ls.providers.get(methods.DEFINITION)
    goto_definition_results = goto_definition_provider.handle_request(ls, params)
    logging.debug(f"Goto Definition results: {goto_definition_results}")
    return goto_definition_results


async def handle_references(ls: AacLanguageServer, params: ReferenceParams):
    """Handle the find references request."""
    find_references_provider = ls.providers.get(methods.REFERENCES)
    find_references_results = find_references_provider.handle_request(ls, params)
    logging.debug(f"Find references results: {find_references_results}")
    return find_references_results


async def handle_rename(ls: AacLanguageServer, params: RenameParams):
    """Handle the rename definition request."""
    rename_provider = ls.providers.get(methods.RENAME)
    rename_results = rename_provider.handle_request(ls, params)
    logging.debug(f"Rename results: {rename_results}")
    return rename_results


async def handle_prepare_rename(ls: AacLanguageServer, params: RenameParams):
    """Handle the prepare rename definition request."""
    prepare_rename_provider = ls.providers.get(methods.PREPARE_RENAME)
    prepare_rename_results = prepare_rename_provider.handle_request(ls, params)
    logging.debug(f"Prepare rename results: {prepare_rename_results}")
    return prepare_rename_results


async def handle_semantic_tokens(ls: AacLanguageServer, params: SemanticTokensParams):
    """Handle the semantic tokens request."""
    semantic_tokens_provider = ls.providers.get(methods.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL)
    semantic_tokens_results = semantic_tokens_provider.handle_request(ls, params)
    logging.debug(f"Semantic tokens results: {semantic_tokens_results}")
    return semantic_tokens_results


async def handle_publish_diagnostics(ls: AacLanguageServer, params: PublishDiagnosticsParams):
    """Handle the publish diagnostics request."""
    publish_diagnostics_provider = ls.providers.get(methods.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)
    diagnostics_results = await publish_diagnostics_provider.handle_request(ls, params)
    logging.debug(f"Publish Diagnostics results: {diagnostics_results}")
    return diagnostics_results
