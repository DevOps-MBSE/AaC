from pygls.lsp import Diagnostic, DiagnosticSeverity, Position, Range, methods
from unittest.async_case import IsolatedAsyncioTestCase

from aac.io.constants import DEFINITION_SEPARATOR
from aac.lang.constants import ROOT_KEY_MODEL
from aac.plugins.first_party.lsp_server.providers.publish_diagnostics_provider import PublishDiagnosticsProvider
from aac.plugins.validators.defined_references import PLUGIN_NAME as DEFINED_REFERENCES_VALIDATOR
from aac.plugins.validators.required_fields import PLUGIN_NAME as REQUIRED_FIELDS_VALIDATOR
from aac.plugins.validators.root_keys import PLUGIN_NAME as ROOT_KEYS_VALIDATOR

from tests.helpers.parsed_definitions import (
    create_enum_definition,
    create_field_entry,
    create_schema_definition,
    create_behavior_entry,
    create_model_definition,
)
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import TEST_DOCUMENT_NAME


class TestPublishDiagnosticsProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    provider: PublishDiagnosticsProvider

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.provider = self.client.lsp_server.providers.get(methods.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)

    async def publish_diagnostics(self, file_name: str) -> list[Diagnostic]:
        self.provider.language_server = self.client.lsp_server
        return self.provider.get_diagnostics(self.to_uri(file_name))

    async def test_get_diagnostics_for_document_with_valid_definitions(self):
        diagnostics = await self.publish_diagnostics(TEST_DOCUMENT_NAME)
        error_diagnostics = [diagnostic for diagnostic in diagnostics if diagnostic.severity == DiagnosticSeverity.Error]
        self.assertListEqual([], error_diagnostics)

    async def test_get_diagnostics_for_document_with_invalid_enum(self):
        invalid_enum_document_name = "enum.aac"

        invalid_enum = create_enum_definition("InvalidEnum", [])
        del invalid_enum.structure[invalid_enum.get_root_key()]["values"]

        await self.create_document(invalid_enum_document_name, invalid_enum.to_yaml())

        diagnostics = await self.publish_diagnostics(invalid_enum_document_name)
        diagnostic, *_ = [diagnostic for diagnostic in diagnostics if diagnostic.severity == DiagnosticSeverity.Error]
        self.assertEqual(0, len(_))
        self.assertEqual(DiagnosticSeverity.Error, diagnostic.severity)
        self.assertEqual(Range(start=Position(line=0, character=0), end=Position(line=0, character=4)), diagnostic.range)
        self.assertEqual(REQUIRED_FIELDS_VALIDATOR, diagnostic.code)
        self.assertRegexpMatches(diagnostic.message.lower(), "required.*values.*missing")

    async def test_get_diagnostics_for_document_with_invalid_schema(self):
        invalid_schema_document_name = "schema.aac"
        fields = [create_field_entry("name", "invalid")]
        invalid_schema = create_schema_definition(name="InvalidSchema", description="a schema with an invalid field", fields=fields)
        await self.create_document(invalid_schema_document_name, invalid_schema.to_yaml())

        diagnostics = await self.publish_diagnostics(invalid_schema_document_name)
        error_diagnostics, *_ = [diagnostic for diagnostic in diagnostics if diagnostic.severity == DiagnosticSeverity.Error]
        self.assertEqual(0, len(_))
        self.assertEqual(DiagnosticSeverity.Error, error_diagnostics.severity)
        self.assertEqual(Range(start=Position(line=5, character=10), end=Position(line=5, character=17)), error_diagnostics.range)
        self.assertEqual(DEFINED_REFERENCES_VALIDATOR, error_diagnostics.code)
        self.assertRegexpMatches(error_diagnostics.message.lower(), "undefined.*invalid.*reference")

    async def test_get_diagnostics_for_document_with_multiple_definitions(self):
        schema_a = create_schema_definition(name="a", description="a schema", fields=[create_field_entry("value", "int")])
        schema_b = create_schema_definition(name="b", description="b schema", fields=[create_field_entry("value", "int")])
        behavior = create_behavior_entry(
            "TheBehavior",
            input=[create_field_entry("in", schema_a.name)],
            output=[create_field_entry("out", schema_b.name)],
        )
        invalid_model_document_name = "multiple.aac"
        invalid_model = create_model_definition(name="InvalidModel", description="an invalid model", behavior=[behavior])
        invalid_model.structure["not_a_valid_root_key"] = invalid_model.structure[ROOT_KEY_MODEL]
        invalid_model.structure.pop(ROOT_KEY_MODEL)

        content = DEFINITION_SEPARATOR.join([schema_a.to_yaml(), schema_b.to_yaml(), invalid_model.to_yaml()])
        await self.create_document(invalid_model_document_name, content)

        diagnostics = await self.publish_diagnostics(invalid_model_document_name)
        error_diagnostic, *_ = [diagnostic for diagnostic in diagnostics if diagnostic.severity == DiagnosticSeverity.Error]
        self.assertEqual(0, len(_))
        self.assertEqual(DiagnosticSeverity.Error, error_diagnostic.severity)
        self.assertEqual(Range(start=Position(line=16, character=0), end=Position(line=16, character=len("not_a_valid_root_key"))), error_diagnostic.range)
        self.assertEqual(ROOT_KEYS_VALIDATOR, error_diagnostic.code)
        self.assertRegexpMatches(error_diagnostic.message.lower(), "undefined.*root.*not_a_valid_root_key")
