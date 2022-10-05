"""A module containing a base LSP provider."""

from abc import abstractmethod

from pygls.lsp.types.basic_structures import Model
from pygls.server import LanguageServer


class LspProvider:
    """A base class used to handle specific LSP requests."""

    @abstractmethod
    def handle_request(self, language_server: LanguageServer, params: Model):
        """Handle the specific request."""
        raise NotImplementedError("All LspProviders must implement the handle_request method.")
