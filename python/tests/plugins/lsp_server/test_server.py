from unittest.async_case import IsolatedAsyncioTestCase

from aac.io.constants import YAML_DOCUMENT_SEPARATOR

from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import (
    TEST_DOCUMENT_NAME,
    TEST_DOCUMENT_CONTENT,
    TEST_SCHEMA_C,
    TEST_SERVICE_TWO,
    TEST_MALFORMED_CONTENT,
    MALFORMED_EXTRA_FIELD_NAME,
    MALFORMED_EXTRA_FIELD_CONTENT,
    TEST_SERVICE_TWO_NAME,
)


class TestLspServer(BaseLspTestCase, IsolatedAsyncioTestCase):
    additional_content = f"{TEST_SCHEMA_C.to_yaml()}{YAML_DOCUMENT_SEPARATOR}{TEST_SERVICE_TWO.to_yaml()}"

    async def test_adds_definitions_when_opening_file(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_SCHEMA_C.name))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_SERVICE_TWO.name))

        await self.create_document("added.aac", self.additional_content)

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_SCHEMA_C.name))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_SERVICE_TWO.name))

    async def test_handles_content_changes(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_SCHEMA_C.name))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_SERVICE_TWO.name))

        await self.write_document(TEST_DOCUMENT_NAME, f"{TEST_DOCUMENT_CONTENT}{YAML_DOCUMENT_SEPARATOR}{self.additional_content}")

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_SCHEMA_C.name))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_SERVICE_TWO.name))

    async def test_handles_content_changes_with_malformed_data(self):
        await self.write_document(TEST_DOCUMENT_NAME, f"{TEST_DOCUMENT_CONTENT}{YAML_DOCUMENT_SEPARATOR}{TEST_MALFORMED_CONTENT}")

        modified_definition = self.active_context.get_definition_by_name(TEST_SERVICE_TWO_NAME)
        modified_definition_content = modified_definition.to_yaml()

        self.assertNotIn(MALFORMED_EXTRA_FIELD_NAME, modified_definition_content)
        self.assertNotIn(MALFORMED_EXTRA_FIELD_CONTENT, modified_definition_content)
