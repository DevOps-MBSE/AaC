"""The Architecture-as-Code Language Server."""

from attr import attrib, attrs, validators
import logging
from typing import Optional
from pygls.server import LanguageServer
from pygls.lsp import (
    CompletionOptions,
    CompletionParams,
    Hover,
    HoverParams,
    InitializeParams,
    InitializeResult,
    ServerCapabilities,
    methods
)

from aac.lang.active_context_lifecycle_manager import get_initialized_language_context
from aac.lang.language_context import LanguageContext
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

    def __attrs_post_init__(self):
        """Post init hook for attrs classes."""
        self.configure_lsp()

    def configure_lsp(self):
        """Configure and setup the LSP server so that it's ready to execute."""
        self.language_context = get_initialized_language_context()
        self.language_server = self.language_server or LanguageServer()
        self.code_completion_provider = self.code_completion_provider or CodeCompletionProvider()
        self.setup_features()

        logging.debug("AaC LSP initialized.")

    def setup_features(self) -> None:
        """Configure the server with the supported features."""
        server = self.language_server

        @server.feature(methods.INITIALIZE)
        async def handle_initialize(ls: LanguageServer, params: InitializeParams):
            """Handle initialize request."""
            return InitializeResult(capabilities=ServerCapabilities(hover_provider=True))

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
