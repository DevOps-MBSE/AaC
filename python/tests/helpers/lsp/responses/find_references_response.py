from pygls.lsp.types import Location

from tests.helpers.lsp.responses.lsp_response import LspResponse


class FindReferencesResponse(LspResponse):
    def get_locations(self) -> list[Location]:
        """Returns a list of tuples consisting of a uri and a range."""
        return [Location(uri=location.get("uri"), range=location.get("range")) for location in self.response]
