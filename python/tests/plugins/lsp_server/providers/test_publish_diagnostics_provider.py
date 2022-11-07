from typing import Optional
from pygls.lsp import Diagnostic, DiagnosticSeverity, Position, PublishDiagnosticsParams, Range, methods
from unittest.async_case import IsolatedAsyncioTestCase

from aac.io.constants import DEFINITION_SEPARATOR
from aac.plugins.first_party.lsp_server.providers.publish_diagnostics_provider import PublishDiagnosticsProvider
from aac.plugins.validators.defined_references import PLUGIN_NAME as DEFINED_REFERENCES_VALIDATOR
from aac.plugins.validators.required_fields import PLUGIN_NAME as REQUIRED_FIELDS_VALIDATOR
from aac.plugins.validators.root_keys import PLUGIN_NAME as ROOT_KEYS_VALIDATOR

from tests.helpers.parsed_definitions import create_enum_definition, create_field_entry, create_schema_definition
from tests.plugins.lsp_server.definition_constants import TEST_DOCUMENT_NAME, TEST_ENUM, TEST_SERVICE_ONE
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase


class TestPublishDiagnosticsProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    provider: PublishDiagnosticsProvider

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.provider = self.client.server.providers.get(methods.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)

    async def publish_diagnostics(self, file_name: str, diagnostics: Optional[list[Diagnostic]] = None) -> list[Diagnostic]:
        return await self.provider.handle_request(
            self.client.server,
            PublishDiagnosticsParams(uri=self.to_uri(file_name), diagnostics=diagnostics or []),
        )

    async def test_get_diagnostics_for_empty_document(self):
        empty_document_name = "empty.aac"
        await self.create_document(empty_document_name)

        diagnostics = await self.publish_diagnostics(empty_document_name)
        self.assertListEqual([], diagnostics)

    async def test_get_diagnostics_for_document_with_valid_definitions(self):
        diagnostics = await self.publish_diagnostics(TEST_DOCUMENT_NAME)
        self.assertListEqual([], diagnostics)

    async def test_get_diagnostics_for_document_with_invalid_enum(self):
        invalid_enum_document_name = "enum.aac"

        invalid_enum = create_enum_definition("InvalidEnum", [])
        del invalid_enum.structure[invalid_enum.get_root_key()]["values"]

        await self.create_document(invalid_enum_document_name, invalid_enum.to_yaml())

        diagnostic, *_ = await self.publish_diagnostics(invalid_enum_document_name)
        self.assertEqual(0, len(_))
        self.assertEqual(DiagnosticSeverity.Error, diagnostic.severity)
        self.assertEqual(Range(start=Position(line=0, character=0), end=Position(line=0, character=4)), diagnostic.range)
        self.assertEqual(REQUIRED_FIELDS_VALIDATOR, diagnostic.code)
        self.assertRegexpMatches(diagnostic.message.lower(), "required.*values.*missing")

    async def test_get_diagnostics_for_document_with_invalid_schema(self):
        invalid_schema_document_name = "schema.aac"
        fields = [create_field_entry("name", "invalid")]
        invalid_schema = create_schema_definition("InvalidSchema", "a schema with an invalid field", fields)
        await self.create_document(invalid_schema_document_name, invalid_schema.to_yaml())

        diagnostic, *_ = await self.publish_diagnostics(invalid_schema_document_name)
        self.assertEqual(0, len(_))
        self.assertEqual(DiagnosticSeverity.Error, diagnostic.severity)
        self.assertEqual(Range(start=Position(line=5, character=10), end=Position(line=5, character=17)), diagnostic.range)
        self.assertEqual(DEFINED_REFERENCES_VALIDATOR, diagnostic.code)
        self.assertRegexpMatches(diagnostic.message.lower(), "undefined.*invalid.*reference")

    async def test_get_diagnostics_for_document_with_multiple_definitions(self):
        TEST_SERVICE_ONE.structure["service"] = TEST_SERVICE_ONE.structure["model"]
        TEST_SERVICE_ONE.structure.pop("model")

        content = DEFINITION_SEPARATOR.join([TEST_ENUM.to_yaml(), TEST_SERVICE_ONE.to_yaml()])
        await self.write_document(TEST_DOCUMENT_NAME, content)

        diagnostic, *_ = await self.publish_diagnostics(TEST_DOCUMENT_NAME)
        self.assertEqual(0, len(_))
        self.assertEqual(DiagnosticSeverity.Error, diagnostic.severity)
        self.assertEqual(Range(start=Position(line=7, character=0), end=Position(line=7, character=7)), diagnostic.range)
        self.assertEqual(ROOT_KEYS_VALIDATOR, diagnostic.code)
        self.assertRegexpMatches(diagnostic.message.lower(), "undefined.*root.*service")
