from unittest.async_case import IsolatedAsyncioTestCase

from tests.lang.lsp.base_lsp_test_case import (
    BaseLspTestCase,
    TEST_DOCUMENT_NAME,
    TEST_DOCUMENT_CONTENT,
    TEST_DOCUMENT_ADDITIONAL_CONTENT,
    TEST_ADDITIONAL_SCHEMA_NAME,
    TEST_ADDITIONAL_MODEL_NAME,
)


class TestLspServer(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def test_adds_definitions_when_opening_file(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

        await self.create_document("added.aac", TEST_DOCUMENT_ADDITIONAL_CONTENT)

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

    async def test_handles_content_changes(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))

        await self.write_document(TEST_DOCUMENT_NAME, f"{TEST_DOCUMENT_CONTENT}---{TEST_DOCUMENT_ADDITIONAL_CONTENT}")

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_SCHEMA_NAME))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_ADDITIONAL_MODEL_NAME))
