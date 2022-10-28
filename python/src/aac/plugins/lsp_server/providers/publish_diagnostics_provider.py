"""Module for PublishDiagnostics Provider which handles publishing of diagnostics for AaC Language Server."""

from pygls.server import LanguageServer
from pygls.lsp.types.basic_structures import Position, Range
from pygls.lsp.types.basic_structures import Diagnostic

from aac.plugins.lsp_server.providers.lsp_provider import LspProvider
from aac.validate._validate import validated_source


class PublishDiagnosticsProvider(LspProvider):
    """Handler for Publishing Diagnostics for AaC LSP."""
    ls = LanguageServer

    async def handle_request(self, ls: LanguageServer, file_uri: str) -> list[Diagnostic]:
        """
        Return the ValidationResults and pass those in through the Diagnostic Module to then be returned and shown to the user through the Editor.

        Args:
            ls (LanguageServer): Contents of the LanguageServer is being passed in.
            file_uri (str): The uri of the file that is currently open or being altered.    

        Returns:
            A list of diagnostics from the ValidationResults. If nothing is found an empty list is returned.
        """
        diagnostics = []
        ls.show_message("Validating AaC Open AaC File...")
        with validated_source(file_uri) as validation_result:
            for finding in validation_result.findings.findings:
                severity = finding.severity
                source = finding.source

                range_start = Position(
                    line=finding.location.line,
                    character=finding.location.position
                )
                range_end = Position(
                    line=finding.location.line,
                    character=finding.location.position+finding.location.span
                )

                message = finding.message
                full_range = Range(
                    start=range_start,
                    end=range_end
                )
            diagnostics.append(Diagnostic(severity=severity, source=source, range=full_range, message=message))
        return diagnostics
