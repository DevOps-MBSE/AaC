from unittest.mock import MagicMock, patch

from aac.parser import parse

from tests.lang.base_lsp_test_case import BaseLspTestCase


class TestLspServer(BaseLspTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.document = self.create_document("test.aac", TEST_DOCUMENT_CONTENT)

    @patch("aac.lang.language_context.LanguageContext.update_definitions_in_context")
    def test_handles_content_changes(self, update_definitions: MagicMock):
        new_content = f"{TEST_DOCUMENT_CONTENT}---{TEST_DOCUMENT_ADDITIONAL_CONTENT}"
        self.write_document(new_content)

        self.assertEqual(new_content, self.read_document())
        update_definitions.assert_called_once_with(parse(new_content))

    def test_handles_hover_request(self):
        res = self.hover(self.document.file_name)

        self.assertSequenceEqual(list(res.keys()), ["contents"])
        self.assertIn("LSP server", res.get("contents"))


TEST_DOCUMENT_CONTENT = """
schema:
  name: DataA
  fields:
  - name: msg
    type: string
---
schema:
  name: DataB
  fields:
  - name: msg
    type: string
---
model:
  name: ServiceOne
  behavior:
    - name: Process DataA Request
      type: request-response
      description: Process a DataA request and return a DataB response
      input:
        - name: in
          type: DataA
      output:
        - name: out
          type: DataB
      acceptance:
        - scenario: Receive DataA request and return DataB response
          given:
            - ServiceOne is running
          when:
            - ServiceOne receives a DataA request
          then:
            - ServiceOne processes the request into a DataB response
            - ServiceOne returns the DataB response
        - scenario: Receive invalid request
          given:
            - ServiceOne is running
          when:
            - ServiceOne receives request that isn't a DataA request
          then:
            - ServiceOne returns an error response code
"""

TEST_DOCUMENT_ADDITIONAL_CONTENT = """
schema:
  name: DataC
  fields:
  - name: msg
    type: string
---
model:
  name: ServiceTwo
  behavior:
    - name: Process DataB Request
      type: request-response
      description: Process a DataB request and return a DataC response
      input:
        - name: in
          type: DataB
      output:
        - name: out
          type: DataC
      acceptance:
        - scenario: Receive DataB request and return DataC response
          given:
            - ServiceTwo is running
          when:
            - ServiceTwo receives a DataB request
          then:
            - ServiceTwo processes the request into a DataC response
            - ServiceTwo returns the DataC response
"""
