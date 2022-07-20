from unittest.async_case import IsolatedAsyncioTestCase

from pygls.lsp import methods
from pygls.lsp.types.basic_structures import Location, Position
from pygls.lsp.types.language_features.definition import DefinitionParams

from aac.spec.core import get_aac_spec_as_yaml
from aac.lang.lsp.providers.goto_definition_provider import GotoDefinitionProvider
from aac.io.constants import YAML_DOCUMENT_SEPARATOR

from tests.helpers.lsp.responses.goto_definition_response import GotoDefinitionResponse
from tests.lang.lsp.base_lsp_test_case import BaseLspTestCase
from tests.lang.lsp.definition_constants import (
    TEST_DOCUMENT_NAME,
    TEST_DOCUMENT_CONTENT,
    TEST_ENUM,
    TEST_SCHEMA_A,
    TEST_SCHEMA_C,
    TEST_SERVICE_THREE,
    TEST_PARTIAL_CONTENT,
)


class TestGotoDefinitionProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    provider: GotoDefinitionProvider

    def get_definition_location_at_position(self, file_name: str, line: int = 0, character: int = 0) -> list[Location]:
        return self.provider.get_definition_location_at_position(
            {self.to_uri(name) or "": self.virtual_document_to_lsp_document(name) for name in self.documents.keys()},
            self.to_uri(file_name) or "",
            Position(line=line, character=character),
        )

    def get_definition_location_of_name(self, name: str) -> list[Location]:
        return self.provider.get_definition_location_of_name(
            {self.to_uri(name) or "": self.virtual_document_to_lsp_document(name) for name in self.documents.keys()},
            name,
        )

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.provider = self.client.server.providers.get(methods.DEFINITION)
        self.provider.language_server = self.client.server

    async def goto_definition(self, file_name: str, line: int = 0, character: int = 0) -> GotoDefinitionResponse:
        """
        Send a goto definition request and return the response.

        Args:
            file_name (str): The name of the virtual document in which to perform the goto definition action.
            line (int): The line number (starting from 0) at which to perform the goto definition action.
            character (int): The character number (starting from 0) at which to perform the goto definition action.

        Returns:
            A GotoDefinitionResponse that is returned from the LSP server.
        """
        return await self.build_request(
            file_name,
            GotoDefinitionResponse,
            methods.DEFINITION,
            DefinitionParams(**self.build_text_document_position_params(file_name, line, character)),
        )

    async def test_get_ranges_containing_name(self):
        text_range, *rest = self.provider.get_ranges_containing_name(TEST_DOCUMENT_CONTENT, TEST_SCHEMA_A.name)
        self.assertEqual(len(rest) + 1, TEST_DOCUMENT_CONTENT.count(TEST_SCHEMA_A.name))

        self.assertEqual(text_range.start, Position(line=1, character=8))
        self.assertEqual(text_range.end, Position(line=1, character=8 + len(TEST_SCHEMA_A.name)))

    async def test_get_named_location(self):
        document_uri = self.to_uri(TEST_DOCUMENT_NAME) or ""
        location, *_ = self.provider.get_definition_location_at_position(
            {document_uri: self.virtual_document_to_lsp_document(TEST_DOCUMENT_NAME)},
            document_uri,
            Position(line=29, character=13),
        )

        self.assertEqual(location.range.start, Position(line=1, character=8))
        self.assertEqual(location.range.end, Position(line=1, character=8 + len(TEST_SCHEMA_A.name)))

    async def test_handles_goto_definition_request_when_cursor_at_definition(self):
        text_range, *_ = self.provider.get_ranges_containing_name(TEST_DOCUMENT_CONTENT, TEST_SCHEMA_A.name)
        line = text_range.start.line
        character = text_range.start.character
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=line, character=character)

        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.range.start, Position(line=line, character=character))
        self.assertEqual(location.range.end, Position(line=line, character=character + len(TEST_SCHEMA_A.name)))

    async def test_handles_goto_definition_request_when_definition_in_same_document(self):
        definition_range, text_range, *_ = self.provider.get_ranges_containing_name(TEST_DOCUMENT_CONTENT, TEST_SCHEMA_A.name)
        line = text_range.start.line
        character = text_range.start.character
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=line, character=character)

        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.range.start, Position(line=definition_range.start.line, character=definition_range.start.character))
        self.assertEqual(location.range.end, Position(line=definition_range.end.line, character=definition_range.end.character))

    async def test_handles_goto_definition_request_when_definition_in_different_document(self):
        added_content = TEST_SCHEMA_C.to_yaml()
        added_document = await self.create_document("added.aac", added_content)

        new_test_document_content = f"{TEST_DOCUMENT_CONTENT}{YAML_DOCUMENT_SEPARATOR}{TEST_SERVICE_THREE.to_yaml()}"
        await self.write_document(TEST_DOCUMENT_NAME, new_test_document_content)

        text_range, *_ = self.provider.get_ranges_containing_name(new_test_document_content, TEST_SCHEMA_C.name)
        line = text_range.start.line
        character = text_range.start.character
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=line, character=character)

        definition_range, *_ = self.provider.get_ranges_containing_name(added_content, TEST_SCHEMA_C.name)

        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.uri, self.to_uri(added_document.file_name))
        self.assertEqual(location.range.start, Position(line=definition_range.start.line, character=definition_range.start.character))
        self.assertEqual(location.range.end, Position(line=definition_range.end.line, character=definition_range.end.character))

    async def test_handles_goto_definition_for_root_keys(self):
        await self.create_document("spec.aac", get_aac_spec_as_yaml())

        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=0, character=1)
        schema_definition_location, *_ = self.get_definition_location_at_position(TEST_DOCUMENT_NAME, line=0, character=1)

        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.uri, self.to_uri(schema_definition_location.uri))
        self.assertEqual(location.range.json(), schema_definition_location.range.json())

    async def test_handles_goto_definition_for_enums(self):
        await self.create_document("spec.aac", get_aac_spec_as_yaml())

        string_range, *_ = self.provider.get_ranges_containing_name(TEST_DOCUMENT_CONTENT, "string")
        line = string_range.start.line
        character = string_range.start.character
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=line, character=character)

        string_definition_location, *_ = self.get_definition_location_of_name("string")
        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.uri, self.to_uri(string_definition_location.uri))
        self.assertEqual(location.range.json(), string_definition_location.range.json())

    async def test_handles_goto_definition_for_symbols_with_hyphens(self):
        await self.create_document("spec.aac", get_aac_spec_as_yaml())

        request_response_range, *_ = self.provider.get_ranges_containing_name(TEST_DOCUMENT_CONTENT, "request-response")
        line = request_response_range.start.line
        character = request_response_range.start.character
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=line, character=character)

        request_response_definition_location, *_ = self.get_definition_location_of_name("request-response")
        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.uri, self.to_uri(request_response_definition_location.uri))
        self.assertEqual(location.range.json(), request_response_definition_location.range.json())

    async def test_handles_goto_definition_for_custom_enums(self):
        await self.create_document("enum.aac", TEST_ENUM.to_yaml())

        new_content = f"{TEST_DOCUMENT_CONTENT}{TEST_PARTIAL_CONTENT} {TEST_ENUM.name}\n"
        await self.write_document(TEST_DOCUMENT_NAME, new_content)

        custom_enum_range, *_ = self.provider.get_ranges_containing_name(new_content, TEST_ENUM.name)
        line = custom_enum_range.start.line
        character = custom_enum_range.start.character
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=line, character=character)

        custom_enum_definition_location, *_ = self.get_definition_location_of_name(TEST_ENUM.name)
        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.uri, self.to_uri(custom_enum_definition_location.uri))
        self.assertEqual(location.range.json(), custom_enum_definition_location.range.json())

    async def test_no_results_when_nothing_under_cursor(self):
        await self.write_document(TEST_DOCUMENT_NAME, f"\n{TEST_DOCUMENT_CONTENT}")
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME)
        self.assertIsNone(res.get_location())
