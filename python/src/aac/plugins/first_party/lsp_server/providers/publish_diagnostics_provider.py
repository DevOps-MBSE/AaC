"""Module for PublishDiagnostics Provider which handles publishing of diagnostics for AaC Language Server."""

from aac.io.parser import parse
from typing import Optional

from pygls.lsp import Diagnostic, DiagnosticSeverity, Position, PublishDiagnosticsParams, Range
from pygls.server import LanguageServer
from pygls.uris import to_fs_path

from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider
from aac.plugins.validators import ValidatorResult
from aac.plugins.validators._validator_finding import FindingSeverity
from aac.validate._validate import _validate_definitions


class PublishDiagnosticsProvider(LspProvider):
    """Handler for Publishing Diagnostics for AaC LSP."""

    async def handle_request(self, ls: LanguageServer, params: PublishDiagnosticsParams) -> list[Diagnostic]:
        """Handle publishing validation findings as diagnostics."""
        diagnostics = []
        validation_result: ValidatorResult = _validate_definitions(parse(to_fs_path(params.uri)), validate_context=True)

        for finding in validation_result.findings.findings:
            finding_location = finding.location.location

            range_start = Position(line=finding_location.line, character=finding_location.position)
            range_end = Position(line=finding_location.line, character=finding_location.position + finding_location.span)

            severity = self.finding_severity_to_diagnostic_severity(finding.severity)

            diagnostics.append(
                Diagnostic(
                    range=Range(start=range_start, end=range_end),
                    severity=severity.value if severity else None,
                    code=finding.location.validation_name,
                    source="aac",
                    message=finding.message,
                )
            )

        return diagnostics

    def finding_severity_to_diagnostic_severity(self, finding_severity: FindingSeverity) -> Optional[DiagnosticSeverity]:
        """Return the DiagnosticSeverity that corresponds most closely to the correpsonding FindingSeverity."""
        finding_severity_name = finding_severity.name.title()
        for severity_name in DiagnosticSeverity._member_names_:
            if finding_severity_name in severity_name:
                return DiagnosticSeverity[severity_name]
