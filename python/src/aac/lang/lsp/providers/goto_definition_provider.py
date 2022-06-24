"""Module for the Goto Definition Provider which handles all goto definition requests."""

from typing import Union

from pygls.server import LanguageServer
from pygls.lsp.types.basic_structures import Location, LocationLink
from pygls.lsp.types.language_features.definition import DefinitionParams

from aac.lang.lsp.providers.lsp_provider import LspProvider


class GotoDefinitionProvider(LspProvider):
    """Resolve the location where a specified name is defined."""

    def handle_request(self, ls: LanguageServer, params: DefinitionParams) -> Union[Location, list[Location], list[LocationLink], None]:
        """Return the location at which the specified item is found."""
        pass
