"""Module for the Code Completion Provider which handles all code completion requests."""

import os
import logging
from attr import Factory, attrib, attrs, validators

from pygls.lsp import CompletionParams, CompletionList, CompletionItem, CompletionItemKind
from pygls.server import LanguageServer

from aac.io.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.definition import Definition
from aac.plugins.first_party.lsp_server.providers.lsp_provider import LspProvider

SPACE_TRIGGER = " "


@attrs
class CodeCompletionProvider(LspProvider):
    """Resolve various code completion triggers to specific code completion functions.

    Attributes:
        completion_callbacks (dict[str, Callable]): The dict of trigger characters to corresponding code completion functions
    """

    completion_callbacks: dict = attrib(default=Factory(dict), validator=validators.instance_of(dict))

    def __attrs_post_init__(self):
        """Post init hook for attrs classes."""
        self.completion_callbacks[SPACE_TRIGGER] = _handle_space_code_completion

    def get_trigger_characters(self) -> list[str]:
        """Return a list of the currently registered trigger characters."""
        return list(self.completion_callbacks.keys())

    def handle_request(self, language_server: LanguageServer, params: CompletionParams):
        """Resolve the trigger to the corresponding code completion function, then execute it."""
        trigger_character = params.context.trigger_character

        if not trigger_character:
            source_document_content = _get_code_completion_parent_text_file(language_server, params).split(os.linesep)
            trigger_character = source_document_content[params.position.line][params.position.character - 1]

        callback_function = self.completion_callbacks.get(trigger_character)
        if callback_function:
            return callback_function(language_server, params)
        else:
            logging.debug(
                f"Failed to find corresponding code completion function for the registered trigger: {trigger_character} in registered callbacks: {self.completion_callbacks}"
            )


def _handle_space_code_completion(language_server: LanguageServer, params: CompletionParams):
    source_document_content = _get_code_completion_parent_text_file(language_server, params).split(os.linesep)
    position_line = source_document_content[params.position.line]

    if position_line.strip().startswith("type:"):
        return _get_reference_completion_items(language_server, params)


def _get_reference_completion_items(language_server: LanguageServer, params: CompletionParams):
    active_context = get_active_context()
    primitives_definition = active_context.get_primitives_definition()

    primitive_references = {}
    if primitives_definition:
        primitive_references = {field: "Primitive type" for field in active_context.get_primitive_types()}

    schema_definition_references = _convert_definitions_to_name_description_dict(
        active_context.get_definitions_by_root_key("schema")
    )

    file_definitions = parse(_get_code_completion_parent_text_file(language_server, params))
    file_schema_references = _convert_definitions_to_name_description_dict(
        get_definitions_by_root_key("schema", file_definitions)
    )
    available_references = primitive_references | schema_definition_references | file_schema_references

    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(label=name, kind=CompletionItemKind.Reference, documentation=description)
            for name, description in available_references.items()
        ],
    )


def _get_code_completion_parent_text_file(language_server: LanguageServer, params: CompletionParams):
    return language_server.workspace.documents.get(params.text_document.uri).source


def _convert_definitions_to_name_description_dict(definitions: list[Definition]) -> dict:
    return {definition.name: definition.get_top_level_fields().get("description") or "" for definition in definitions}
