"""Module for PublishDiagnostics Provider which handles publishing of diagnostics for AaC Language Server."""

from aac.io.parser import parse
from typing import Optional

from pygls.lsp import Diagnostic, DiagnosticSeverity, PublishDiagnosticsParams
from pygls.server import LanguageServer
from pygls.uris import to_fs_path

from aac.plugins.first_party.lsp_server.conversion_helpers import source_location_to_range
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider
from aac.plugins.validators._validator_finding import ValidatorFinding, FindingSeverity
from aac.validate._validate import _validate_definitions


class PublishDiagnosticsProvider(LspProvider):
    """Handler for Publishing Diagnostics for AaC LSP."""

    diagnostics: list[Diagnostic] = []

    async def handle_request(self, _: LanguageServer, params: PublishDiagnosticsParams) -> list[Diagnostic]:
        """Handle publishing validation findings as diagnostics."""

        def finding_to_diagnostic(finding: ValidatorFinding):
            severity = self.finding_severity_to_diagnostic_severity(finding.severity)
            return Diagnostic(
                range=source_location_to_range(finding.location.location),
                severity=severity.value if severity else None,
                code=finding.location.validation_name,
                source="aac",
                message=finding.message,
            )

        result = _validate_definitions(parse(to_fs_path(params.uri)), validate_context=True)
        self.diagnostics.extend([finding_to_diagnostic(finding) for finding in result.findings.get_all_findings()])
        return self.diagnostics

    def finding_severity_to_diagnostic_severity(self, finding_severity: FindingSeverity) -> Optional[DiagnosticSeverity]:
        """Return the DiagnosticSeverity that corresponds most closely to the correpsonding FindingSeverity."""
        finding_severity_name = finding_severity.name.title()
        for severity_name in DiagnosticSeverity._member_names_:
            if finding_severity_name in severity_name:
                return DiagnosticSeverity[severity_name]
