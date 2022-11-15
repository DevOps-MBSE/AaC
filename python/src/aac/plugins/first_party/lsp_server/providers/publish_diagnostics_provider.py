"""Module for PublishDiagnostics Provider which handles publishing of diagnostics for AaC Language Server."""

from typing import Optional

from pygls.lsp import Diagnostic, DiagnosticSeverity, PublishDiagnosticsParams
from pygls.server import LanguageServer
from pygls.uris import to_fs_path

from aac.io.parser import parse
from aac.plugins.first_party.lsp_server.conversion_helpers import source_location_to_range
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider
from aac.plugins.validators._validator_finding import ValidatorFinding, FindingSeverity
from aac.validate._validate import _validate_definitions


class PublishDiagnosticsProvider(LspProvider):
    """Handler for Publishing Diagnostics for AaC LSP."""

    async def handle_request(self, ls: LanguageServer, params: PublishDiagnosticsParams) -> list[Diagnostic]:
        """Handle publishing validation findings as diagnostics."""
        self.language_server = ls
        diagnostics = self.get_diagnostics(params.uri)
        ls.publish_diagnostics(params.uri, diagnostics)
        return diagnostics

    def get_diagnostics(self, document_uri: str) -> list[Diagnostic]:
        """Add the Diagnostics found on document_uri."""
        findings = self.get_findings_for_document(document_uri)
        return [self.finding_to_diagnostic(finding) for finding in findings]

    def get_findings_for_document(self, document_uri: str) -> list[ValidatorFinding]:
        """Return all the ValidatorFindings for the specified document."""
        document = self.language_server.workspace.get_document(document_uri)
        parsed_definitions = parse(document.source, to_fs_path(document_uri))
        result = _validate_definitions(parsed_definitions, self.language_server.language_context, validate_context=False)
        return result.findings.get_all_findings()

    def finding_to_diagnostic(self, finding: ValidatorFinding) -> Diagnostic:
        """Convert a ValidatorFinding to an LSP Diagnostic."""
        severity = self.finding_severity_to_diagnostic_severity(finding.severity)
        return Diagnostic(
            range=source_location_to_range(finding.location.location),
            severity=severity.value if severity else None,
            code=finding.location.validation_name,
            source="aac",
            message=finding.message,
        )

    def finding_severity_to_diagnostic_severity(self, finding_severity: FindingSeverity) -> Optional[DiagnosticSeverity]:
        """Return the DiagnosticSeverity that corresponds most closely to the correpsonding FindingSeverity."""
        finding_severity_name = finding_severity.name.title()
        for severity_name in DiagnosticSeverity._member_names_:
            if finding_severity_name in severity_name:
                return DiagnosticSeverity[severity_name]
