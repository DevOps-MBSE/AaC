"""Module for the Semantic Tokens Provider which handles."""

from typing import Any, Callable, Optional

from pygls.lsp import SemanticTokenModifiers, SemanticTokenTypes, SemanticTokens, SemanticTokensLegend, SemanticTokensParams
from pygls.server import LanguageServer
from pygls.uris import to_fs_path
from yaml import Token

from aac.io.parser._parse_source import _scan_yaml
from aac.lang.language_context import LanguageContext
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider
from aac.spec.core import get_root_keys, _get_aac_spec_file_path


def _is_enum(token: Token, language_context: LanguageContext) -> bool:
    """Return whether the provided token is an Enum token type."""
    definition = language_context.get_definition_by_name(token.value)
    return definition.is_enum() if definition else False


def _is_enum_member(token: Token, language_context: LanguageContext) -> bool:
    """Return whether the provided token is a value defined by an enum."""
    return language_context.get_enum_definition_by_type(token.value)


def _is_keyword(token: Token, language_context: LanguageContext) -> bool:
    """Return whether the provided token is an AaC keyword."""
    return token.value in language_context.get_root_keys()


def _is_struct(token: Token, language_context: LanguageContext) -> bool:
    """Return whether the provided token is a Struct token type."""
    definition = language_context.get_definition_by_name(token.value)
    return definition.is_schema() if definition else False


def _is_string(token: Token, language_context: LanguageContext) -> bool:
    """Return whether the provided token represents a string value."""
    is_explicit_string = hasattr(token, "style") and token.style and token.style in "|'\""
    contains_spaces = any(map(lambda ch: ch.isspace(), token.value))
    return is_explicit_string or contains_spaces


def _is_macro(token: Token, language_context: LanguageContext) -> bool:
    """Return whether the provided token represents a Macro semantic token."""
    definition = language_context.get_definition_by_name(token.value)
    return definition.get_root_key() in get_root_keys() if definition else False


def _is_readonly(token: Token, language_context: LanguageContext) -> bool:
    """Return whether the provided token is readonly."""
    definition = (
        language_context.get_enum_definition_by_type(token.value)
        if _is_enum_member(token, language_context)
        else language_context.get_definition_by_name(token.value)
    )
    return _is_from_default_library(token, language_context) or not definition.source.is_user_editable if definition else False


def _is_from_default_library(token: Token, language_context: LanguageContext) -> bool:
    """Return whether the provided token is built-in to the AaC core spec."""
    is_root_key = token.value in get_root_keys()
    enum_definition = language_context.get_enum_definition_by_type(token.value)
    return is_root_key or (enum_definition.source.uri == _get_aac_spec_file_path() if enum_definition else False)


class SemanticTokensProvider(LspProvider):
    """Return semantic tokens for the provided."""

    token_types = {
        SemanticTokenTypes.Enum: _is_enum,
        SemanticTokenTypes.EnumMember: _is_enum_member,
        SemanticTokenTypes.Keyword: _is_keyword,
        SemanticTokenTypes.Struct: _is_struct,
        SemanticTokenTypes.String: _is_string,
        SemanticTokenTypes.Macro: _is_macro,
    }
    token_modifiers = {
        SemanticTokenModifiers.Readonly: _is_readonly,
        SemanticTokenModifiers.DefaultLibrary: _is_from_default_library,
    }

    def handle_request(self, language_server: LanguageServer, params: SemanticTokensParams) -> SemanticTokens:
        """Handle the semantic tokens request."""
        self.language_server = language_server

        token_data = []
        with open(to_fs_path(params.text_document.uri), mode="r") as file:
            prev_token, *tokens = _scan_yaml(file.read())
            tokens = [token for token in tokens if hasattr(token, "value")]
            for token in tokens:
                semantic_token_data = self.convert_to_semantic_token(prev_token, token)
                if semantic_token_data:
                    token_data.extend(list(semantic_token_data))
                    prev_token = token

            return SemanticTokens(data=token_data)

    def get_semantic_tokens_legend(self) -> SemanticTokensLegend:
        """Return the legend for interpreting the semantic tokens codes."""

        def get_names(values) -> list[str]:
            return [value.name for value in values]

        return SemanticTokensLegend(
            token_types=get_names(self.token_types.keys()),
            token_modifiers=get_names(self.token_modifiers.keys()),
        )

    def get_relative_line(self, prev, curr) -> int:
        """Return the current line relative to the previous line."""
        return self.get_line(curr) - self.get_line(prev)

    def get_relative_char(self, prev, curr) -> int:
        """Return the current character relative to the previous character."""

        def is_on_same_line():
            return self.get_line(prev) == self.get_line(curr)

        return self.get_char(curr) - (self.get_char(prev) if is_on_same_line() else 0)

    def get_line(self, token: Token) -> int:
        """Return the line for the provided token."""
        return token.start_mark.line

    def get_char(self, token: Token) -> int:
        """Return the starting character for the provided token."""
        return token.start_mark.column

    def get_modifiers_for_token(self, token: Token) -> int:
        """Return an integer whose bits represent which token modifiers apply to the token."""

        def update_modifier_bitmask(index, previous_value):
            return previous_value | (index + 1)

        return self.filter_by_token_properties(token, self.token_modifiers, update_modifier_bitmask, initial_value=0)

    def convert_to_semantic_token(self, prev_token: Token, token: Token) -> Optional[tuple[int, int, int, int, int]]:
        """Convert the token to a semantic token for the LSP."""

        def get_semantic_data_for_token(index, prev_value):
            return prev_value or (
                self.get_relative_line(prev_token, token),
                self.get_relative_char(prev_token, token),
                token.end_mark.index - token.start_mark.index,
                index,
                self.get_modifiers_for_token(token),
            )

        return self.filter_by_token_properties(token, self.token_types, get_semantic_data_for_token)

    def filter_by_token_properties(self, token: Token, token_props: dict, callback: Callable, *, initial_value=None) -> Any:
        """Go through the token properties and find the token test that is satisfied by token."""
        value = initial_value
        for index, token_test in enumerate(token_props.values()):
            if token_test(token, self.language_server.language_context):
                value = callback(index, value)
        return value
