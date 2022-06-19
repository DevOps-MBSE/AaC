from abc import ABC
from typing import Optional


class LspResponse(ABC):
    def __init__(self, response: dict) -> None:
        """
        Create an LSP response object.

        Args:
            response (dict): The response dictionary obtained as a result of the LSP request.
        """
        self.response = response

    def get_content(self) -> Optional[str]:
        return self.response.get("contents")
