from unittest.async_case import IsolatedAsyncioTestCase
from re import search
from os import linesep, path

from pygls.lsp import methods
from pygls.lsp.types import Location, Position, Range, ReferenceContext, ReferenceParams

from tests.helpers.lsp.responses.find_references_response import FindReferencesResponse
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase
from tests.plugins.lsp_server.definition_constants import (
    TEST_DOCUMENT_NAME,
    TEST_DOCUMENT_CONTENT,
    TEST_SCHEMA_B,
)


class TestFindReferencesProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    async def reference(self, file_name: str, line: int = 0, character: int = 0) -> FindReferencesResponse:
        """
        Send a hover request and return the response.

        Args:
            file_name (str): The name of the virtual document in which to perform the hover action.
            line (int): The line number (starting from 0) at which to perform the hover action.
            character (int): The character number (starting from 0) at which to perform the hover action.

        Returns:
            A FindReferencesResponse that is returned from the LSP server.
        """
        return await self.build_request(
            file_name,
            FindReferencesResponse,
            methods.REFERENCES,
            ReferenceParams(
                context=ReferenceContext(include_declaration=True),
                **self.build_text_document_position_params(file_name, line, character)
            ),
        )

    async def test_reference_find_all_definition_references(self):
        expected_locations = []
        substring_index = 0
        match = search(TEST_SCHEMA_B.name, TEST_DOCUMENT_CONTENT)

        while match is not None:
            line = _get_line_for_offset(TEST_DOCUMENT_CONTENT, substring_index)
            last_line_end_index = TEST_DOCUMENT_CONTENT[:substring_index].rindex(linesep) if substring_index > 0 else 0
            line_match = search(TEST_SCHEMA_B.name, TEST_DOCUMENT_CONTENT[last_line_end_index:substring_index])

            if "type:" in TEST_DOCUMENT_CONTENT[last_line_end_index:substring_index]:
                expected_locations.append(
                    Location(
                        uri=self.to_uri(TEST_DOCUMENT_NAME).removeprefix("file://"),
                        range=Range(
                            start=Position(line=line, character=line_match.start() - 1),
                            end=Position(line=line, character=line_match.end() - 1),
                        ),
                    )
                )

            substring_index += match.end()
            match = search(TEST_SCHEMA_B.name, TEST_DOCUMENT_CONTENT[substring_index:])

        selection_line = expected_locations[0].range.start.line
        selection_character = expected_locations[0].range.start.character
        res: FindReferencesResponse = await self.reference(
            TEST_DOCUMENT_NAME, line=selection_line, character=selection_character
        )

        locations = res.get_locations()
        self.assertIsNotNone(locations)
        self.assertGreater(len(locations), 0)
        self.assertListEqual(expected_locations, locations)

    async def test_reference_find_all_root_key_references(self):
        selected_text = "schema"
        expected_locations = []
        substring_index = 0
        match = search(selected_text, TEST_DOCUMENT_CONTENT)

        while match is not None:
            substring_index += match.end()
            line = _get_line_for_offset(TEST_DOCUMENT_CONTENT, substring_index)
            last_line_end_index = 0
            try:
                last_line_end_index = TEST_DOCUMENT_CONTENT[:substring_index].rindex(linesep) + 1
            except ValueError:
                pass

            line_match = search(selected_text, TEST_DOCUMENT_CONTENT[last_line_end_index:substring_index])

            if line_match:
                expected_locations.append(
                    Location(
                        uri=self.to_uri(TEST_DOCUMENT_NAME).removeprefix("file://"),
                        range=Range(
                            start=Position(line=line, character=line_match.start()),
                            end=Position(line=line, character=line_match.end()),
                        ),
                    )
                )

            match = search(selected_text, TEST_DOCUMENT_CONTENT[substring_index:])

        selection_line = expected_locations[0].range.start.line
        selection_character = expected_locations[0].range.start.character
        res: FindReferencesResponse = await self.reference(
            TEST_DOCUMENT_NAME, line=selection_line, character=selection_character
        )

        locations = res.get_locations()
        self.assertIsNotNone(locations)
        self.assertGreater(len(locations), 0)
        # Since the schema keyword is used widely, we're limiting our actual test results to the file under test.
        filtered_actual_locations = [
            location for location in locations if path.basename(location.uri) == path.basename(TEST_DOCUMENT_NAME)
        ]
        self.assertListEqual(expected_locations, filtered_actual_locations)


def _get_line_for_offset(content: str, offset: int) -> int:
    """Returns a line number for the given offset."""
    return len([char for char in content[:offset] if char == linesep])
