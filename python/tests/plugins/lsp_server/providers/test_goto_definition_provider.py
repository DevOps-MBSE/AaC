from os import path
from pygls.lsp import methods
from pygls.lsp.types.basic_structures import Location, Position, Range
from pygls.lsp.types.language_features.definition import DefinitionParams
from unittest.async_case import IsolatedAsyncioTestCase
from re import search

from aac.io.constants import YAML_DOCUMENT_SEPARATOR
from aac.lang.constants import BEHAVIOR_TYPE_REQUEST_RESPONSE, PRIMITIVE_TYPE_STRING
from aac.spec.core import get_aac_spec_as_yaml, _get_aac_spec_file_path
from aac.plugins.first_party.lsp_server.providers.goto_definition_provider import GotoDefinitionProvider

from tests.helpers.lsp.responses.goto_definition_response import GotoDefinitionResponse
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import (
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
            {self.to_uri(name): self.virtual_document_to_lsp_document(name) for name in self.documents.keys()},
            self.to_uri(file_name),
            Position(line=line, character=character),
        )

    def get_definition_location_of_name(self, content: str, name: str) -> Location:
        test_document_lines = content.splitlines()
        target_line = [line for line in test_document_lines if name in line][0]
        match = search(name, target_line)
        line = test_document_lines.index(target_line)
        return Location(
            uri="",
            range=Range(start=Position(line=line, character=match.start()), end=Position(line=line, character=match.end())),
        )

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.provider = self.client.lsp_server.providers.get(methods.DEFINITION)
        self.provider.language_server = self.client.lsp_server

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

    async def test_get_named_location(self):
        document_uri = self.to_uri(path.join(TEST_DOCUMENT_NAME))
        location, *_ = self.provider.get_definition_location_at_position(
            {document_uri: self.virtual_document_to_lsp_document(TEST_DOCUMENT_NAME)},
            document_uri,
            Position(line=25, character=13),
        )

        self.assertEqual(location.range.start, Position(line=1, character=8))
        self.assertEqual(location.range.end, Position(line=1, character=8 + len(TEST_SCHEMA_A.name)))

    async def test_handles_goto_definition_request_when_cursor_at_definition(self):
        target_location = self.get_definition_location_of_name(TEST_DOCUMENT_CONTENT, TEST_SCHEMA_A.name)
        res: GotoDefinitionResponse = await self.goto_definition(
            TEST_DOCUMENT_NAME, line=target_location.range.start.line, character=target_location.range.start.character
        )

        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(
            location.range.start, Position(line=location.range.start.line, character=location.range.start.character)
        )
        self.assertEqual(location.range.end, Position(line=location.range.end.line, character=location.range.end.character))

    async def test_handles_goto_definition_request_when_definition_in_same_document(self):
        target_location = self.get_definition_location_of_name(TEST_DOCUMENT_CONTENT, TEST_SCHEMA_A.name)
        res: GotoDefinitionResponse = await self.goto_definition(
            TEST_DOCUMENT_NAME, line=target_location.range.start.line, character=target_location.range.start.character
        )

        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(
            location.range.start, Position(line=location.range.start.line, character=location.range.start.character)
        )
        self.assertEqual(location.range.end, Position(line=location.range.end.line, character=location.range.end.character))

    async def test_handles_goto_definition_request_when_definition_in_different_document(self):
        added_content = TEST_SCHEMA_C.to_yaml()
        added_document = await self.create_document("added.aac", added_content)

        new_test_document_content = f"{TEST_DOCUMENT_CONTENT}{YAML_DOCUMENT_SEPARATOR}{TEST_SERVICE_THREE.to_yaml()}"
        await self.write_document(TEST_DOCUMENT_NAME, new_test_document_content)

        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=61, character=17)

        expected_location = self.get_definition_location_of_name(added_content, TEST_SCHEMA_C.name)

        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(path.basename(location.uri), path.basename(added_document.file_name))
        self.assertEqual(
            location.range.start,
            Position(line=expected_location.range.start.line, character=expected_location.range.start.character),
        )
        self.assertEqual(
            location.range.end,
            Position(line=expected_location.range.end.line, character=expected_location.range.end.character),
        )

    async def test_handles_goto_definition_for_enums(self):
        string_location = self.get_definition_location_of_name(TEST_DOCUMENT_CONTENT, PRIMITIVE_TYPE_STRING)
        res: GotoDefinitionResponse = await self.goto_definition(
            TEST_DOCUMENT_NAME, string_location.range.start.line, character=string_location.range.start.character
        )

        expected_location = Location(
            uri=_get_aac_spec_file_path(),
            range=Range(start=Position(line=195, character=6), end=Position(line=195, character=12)),
        )
        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.uri, expected_location.uri)
        self.assertEqual(location.range.json(), expected_location.range.json())

    async def test_handles_goto_definition_for_symbols_with_hyphens(self):
        string_location = self.get_definition_location_of_name(TEST_DOCUMENT_CONTENT, BEHAVIOR_TYPE_REQUEST_RESPONSE)
        res: GotoDefinitionResponse = await self.goto_definition(
            TEST_DOCUMENT_NAME, line=string_location.range.start.line, character=string_location.range.start.character
        )

        request_response_definition_location = self.get_definition_location_of_name(
            get_aac_spec_as_yaml(), BEHAVIOR_TYPE_REQUEST_RESPONSE
        )
        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.range.json(), request_response_definition_location.range.json())

    async def test_handles_goto_definition_for_custom_enums(self):
        await self.create_document("enum.aac", TEST_ENUM.to_yaml())

        new_content = f"{TEST_DOCUMENT_CONTENT}{TEST_PARTIAL_CONTENT} {TEST_ENUM.name}\n"
        await self.write_document(TEST_DOCUMENT_NAME, new_content)

        string_location = self.get_definition_location_of_name(new_content, TEST_ENUM.name)
        res: GotoDefinitionResponse = await self.goto_definition(
            TEST_DOCUMENT_NAME, line=string_location.range.start.line, character=string_location.range.start.character
        )

        custom_enum_location = self.get_definition_location_of_name(TEST_ENUM.to_yaml(), TEST_ENUM.name)
        location = res.get_location()
        self.assertIsNotNone(location)
        self.assertEqual(location.range.json(), custom_enum_location.range.json())

    async def test_no_results_when_nothing_under_cursor(self):
        await self.write_document(TEST_DOCUMENT_NAME, f" \n{TEST_DOCUMENT_CONTENT}")
        res: GotoDefinitionResponse = await self.goto_definition(TEST_DOCUMENT_NAME, line=0)
        self.assertIsNone(res.get_location())
