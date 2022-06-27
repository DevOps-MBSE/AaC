class LspResponse:
    def __init__(self, response: dict) -> None:
        """
        Create an LSP response object.

        Args:
            response (dict): The response dictionary obtained as a result of the LSP request.
        """
        self.response = response
