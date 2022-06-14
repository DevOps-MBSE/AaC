from tests.lang.base_lsp_test_case import BaseLspTestCase


class TestLspServer(BaseLspTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.document = self.create_document("test.aac", TEST_DOCUMENT_CONTENT)

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
