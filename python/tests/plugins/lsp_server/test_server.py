from unittest.async_case import IsolatedAsyncioTestCase

from aac.io.constants import DEFINITION_SEPARATOR
from aac.lang.constants import DEFINITION_FIELD_NAME

from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import (
    TEST_DOCUMENT_NAME,
    TEST_SCHEMA_A,
    TEST_SCHEMA_B,
    TEST_SCHEMA_C,
    TEST_SERVICE_ONE,
    TEST_SERVICE_TWO,
)


class TestLspServer(BaseLspTestCase, IsolatedAsyncioTestCase):
    additional_content = f"{TEST_SCHEMA_C.to_yaml()}{DEFINITION_SEPARATOR}{TEST_SERVICE_TWO.to_yaml()}"

    async def test_adds_definitions_when_opening_file(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_SCHEMA_C.name))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_SERVICE_TWO.name))

        await self.create_document("added.aac", self.additional_content)

        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_SCHEMA_C.name))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_SERVICE_TWO.name))

    async def test_handles_content_changes(self):
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_SCHEMA_C.name))
        self.assertIsNone(self.active_context.get_definition_by_name(TEST_SERVICE_TWO.name))

        new_schema_a_field_name = "MESSAGE"
        altered_schema_a = TEST_SCHEMA_A.copy()
        altered_schema_a.get_fields()[0][DEFINITION_FIELD_NAME] = new_schema_a_field_name
        updated_content = DEFINITION_SEPARATOR.join(
            [
                altered_schema_a.to_yaml(),
                TEST_SCHEMA_B.to_yaml(),
                TEST_SCHEMA_C.to_yaml(),
                TEST_SERVICE_ONE.to_yaml(),
                TEST_SERVICE_TWO.to_yaml(),
            ]
        )
        await self.write_document(TEST_DOCUMENT_NAME, updated_content)

        self.assertEqual(
            new_schema_a_field_name,
            self.active_context.get_definition_by_name(TEST_SCHEMA_A.name).get_fields()[0].get(DEFINITION_FIELD_NAME),  ### TODO: POPO update ###
        )
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_SCHEMA_C.name))
        self.assertIsNotNone(self.active_context.get_definition_by_name(TEST_SERVICE_TWO.name))
