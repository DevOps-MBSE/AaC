from pygls.lsp import SemanticTokenTypes, SemanticTokensParams, TextDocumentIdentifier, methods
from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import patch

from aac.io import parser
from aac.io.constants import YAML_DOCUMENT_SEPARATOR
from aac.lang.constants import ROOT_KEY_VALIDATION
from aac.plugins.first_party.lsp_server.providers.semantic_tokens_provider import SemanticTokensProvider

from tests.helpers.lsp.responses.semantic_tokens_response import SemanticTokensResponse
from tests.helpers.parsed_definitions import (
    create_enum_definition,
    create_field_entry,
    create_schema_definition,
    create_validation_entry,
    create_behavior_entry,
    create_model_definition,
)
from tests.plugins.lsp_server.base_lsp_test_case import BaseLspTestCase


class TestSemanticTokensProvider(BaseLspTestCase, IsolatedAsyncioTestCase):
    provider: SemanticTokensProvider

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.provider = self.client.lsp_server.providers.get(methods.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL)
        self.provider.language_server = self.client.lsp_server

    async def semantic_tokens(self, file_name: str) -> SemanticTokensResponse:
        """
        Send a semantic tokens request and return the response.

        Args:
            file_name (str): The name of the virtual document in which to perform the semantic tokens action.

        Returns:
            A SemanticTokensResponse that is returned from the LSP server.
        """
        return await self.build_request(
            file_name,
            SemanticTokensResponse,
            methods.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
            SemanticTokensParams(text_document=TextDocumentIdentifier(uri=self.to_uri(file_name))),
        )

    async def test_get_semantic_tokens_for_empty_document(self):
        empty_document_name = "empty.aac"
        await self.create_document(empty_document_name)

        res: SemanticTokensResponse = await self.semantic_tokens(empty_document_name)
        self.assertListEqual([], res.get_default_data())

    async def test_get_semantic_tokens_for_enum(self):
        enum = create_enum_definition("EnumName", ["a", "be", "see"])

        document_name = "sample.aac"
        await self.create_document(document_name, enum.content)

        res: SemanticTokensResponse = await self.semantic_tokens(document_name)

        props = {
            enum.name: {
                enum.get_root_key(): (SemanticTokenTypes.Keyword, 0b10),
                enum.name: (SemanticTokenTypes.Enum, 0b0),
                **{value: (SemanticTokenTypes.EnumMember, 0b0) for value in enum.get_values()},
            }
        }
        self.assertListEqual(self.get_expected_tokens_from_definitions([enum], props), res.get_semantic_tokens())

    async def test_get_semantic_tokens_for_schema(self):
        fields = [
            create_field_entry(f"Field{i}", type, f"Field{i} of type {type}")
            for i, type in enumerate(["string", "int", "file"])
        ]
        validations = [create_validation_entry("sample validation")]
        schema = create_schema_definition("SchemaName", description="a test schema", fields=fields, validations=validations)

        document_name = "sample.aac"
        await self.create_document(document_name, schema.content)

        res: SemanticTokensResponse = await self.semantic_tokens(document_name)

        props = {
            schema.name: {
                schema.get_root_key(): (SemanticTokenTypes.Keyword, 0b10),
                schema.name: (SemanticTokenTypes.Struct, 0b0),
                schema.get_description(): (SemanticTokenTypes.String, 0b0),
                **{f.get("type"): (SemanticTokenTypes.EnumMember, 0b11) for f in fields},
                **{f.get("description"): (SemanticTokenTypes.String, 0b0) for f in fields},
                ROOT_KEY_VALIDATION: (SemanticTokenTypes.Keyword, 0b10),
                **{v.get("name"): (SemanticTokenTypes.String, 0b0) for v in validations},
            }
        }
        self.assertListEqual(self.get_expected_tokens_from_definitions([schema], props), res.get_semantic_tokens())

    async def test_get_semantic_tokens_for_test_document(self):
        fields = lambda x: [
            create_field_entry(f"Field{i}", type, f"Field{i} of type {type} in schema {x}")
            for i, type in enumerate(["string", "int", "file"])
        ]
        schema1 = create_schema_definition("SchemaOneName", "test schema 1", fields(1))
        schema2 = create_schema_definition("SchemaTwoName", "test schema 2", fields(2))

        behavior = create_behavior_entry(
            "Some behavior",
            description="do something",
            input=[create_field_entry("in", schema1.name, f"take {schema1.name} as an input")],
            output=[create_field_entry("out", schema2.name, f"take {schema2.name} as an output")],
        )
        model = create_model_definition("ServiceOne", "a sample service model", behavior=[behavior])

        document_name = "sample.aac"
        document_content = f"{YAML_DOCUMENT_SEPARATOR}\n".join([schema1.content, schema2.content, model.content])
        await self.create_document(document_name, document_content)

        res: SemanticTokensResponse = await self.semantic_tokens(document_name)

        parsed_definitions = parser.parse(document_content)
        data_a, data_b, service_one = parsed_definitions

        props = {
            data_a.name: {
                data_a.get_root_key(): (SemanticTokenTypes.Keyword, 0b10),
                data_a.name: (SemanticTokenTypes.Struct, 0b0),
                data_a.get_description(): (SemanticTokenTypes.String, 0b0),
                **{f.get("type"): (SemanticTokenTypes.EnumMember, 0b11) for f in data_a.get_fields()},
                **{f.get("description"): (SemanticTokenTypes.String, 0b0) for f in data_a.get_fields()},
            },
            data_b.name: {
                data_b.get_root_key(): (SemanticTokenTypes.Keyword, 0b10),
                data_b.name: (SemanticTokenTypes.Struct, 0b0),
                data_b.get_description(): (SemanticTokenTypes.String, 0b0),
                **{f.get("type"): (SemanticTokenTypes.EnumMember, 0b11) for f in data_b.get_fields()},
                **{f.get("description"): (SemanticTokenTypes.String, 0b0) for f in data_b.get_fields()},
            },
            service_one.name: {
                service_one.get_root_key(): (SemanticTokenTypes.Keyword, 0b10),
                service_one.name: (SemanticTokenTypes.Macro, 0b0),
                service_one.get_description(): (SemanticTokenTypes.String, 0b0),
                behavior.get("name"): (SemanticTokenTypes.String, 0b0),
                behavior.get("type"): (SemanticTokenTypes.EnumMember, 0b11),
                behavior.get("description"): (SemanticTokenTypes.String, 0b0),
                **{i.get("type"): (SemanticTokenTypes.Struct, 0b0) for i in behavior.get("input")},
                **{i.get("description"): (SemanticTokenTypes.String, 0b0) for i in behavior.get("input")},
                **{o.get("type"): (SemanticTokenTypes.Struct, 0b0) for o in behavior.get("output")},
                **{o.get("description"): (SemanticTokenTypes.String, 0b0) for o in behavior.get("output")},
            },
        }
        self.assertListEqual(self.get_expected_tokens_from_definitions(parsed_definitions, props), res.get_semantic_tokens())

    def get_token_from_lexeme(self, prev, lexeme, type, modifier):
        pkg = "aac.plugins.first_party.lsp_server.providers.semantic_tokens_provider.SemanticTokensProvider"
        with patch(f"{pkg}.get_line") as get_line, patch(f"{pkg}.get_char") as get_char:
            get_line.side_effect = lambda lexeme: lexeme.location.line if lexeme else 0
            get_char.side_effect = lambda lexeme: lexeme.location.column if lexeme else 0

            return [
                self.provider.get_relative_line(prev, lexeme),
                self.provider.get_relative_char(prev, lexeme),
                lexeme.location.span,
                list(self.provider.token_types.keys()).index(type),
                modifier,
            ]

    def get_expected_tokens_from_definitions(self, definitions, props) -> list[list[int]]:
        """
        Return the expected semantic tokens from the definitions based on params.

        Args:
            definitions (list[Definition]): The list of definitions for which to calculate the
                                            expected semantic tokens.
            props (dict): A mapping from the name of a definition to expected token values for that
                          definition and the expected type and modifier of that specific token.
        """
        expected_tokens = []
        prev_lexeme = None

        for definition in definitions:
            definition_props = props.get(definition.name)
            lexemes = [lexeme for lexeme in definition.lexemes if lexeme.value in definition_props.keys()]
            expected_tokens.extend(
                [
                    self.get_token_from_lexeme(prev, curr, *definition_props.get(curr.value))
                    for curr, prev in zip(lexemes, [prev_lexeme, *lexemes[:-1]])
                ]
            )
            prev_lexeme = lexemes[-1]

        return expected_tokens
