from typing import Optional
from pygls.lsp import Diagnostic, PublishDiagnosticsParams, methods
from unittest.async_case import IsolatedAsyncioTestCase

from aac.plugins.first_party.lsp_server.providers.publish_diagnostics_provider import PublishDiagnosticsProvider

from tests.helpers.parsed_definitions import create_enum_definition
from tests.plugins.lsp_server.definition_constants import TEST_DOCUMENT_NAME
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

        diagnostics = await self.publish_diagnostics(invalid_enum_document_name)
        self.assertEqual(1, len(diagnostics))
