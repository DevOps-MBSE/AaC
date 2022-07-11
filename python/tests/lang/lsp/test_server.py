from unittest.async_case import IsolatedAsyncioTestCase

from aac.parser._parse_source import YAML_DOCUMENT_SEPARATOR

from tests.lang.lsp.base_lsp_test_case import BaseLspTestCase
from tests.lang.lsp.definition_constants import (
    TEST_DOCUMENT_NAME,
    TEST_DOCUMENT_CONTENT,
    TEST_SCHEMA_C,
    TEST_SERVICE_TWO,
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
