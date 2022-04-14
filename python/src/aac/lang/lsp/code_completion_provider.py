"""Module for the Code Completion Provider which handles all code completion requests."""

import os
import logging
from attr import Factory, attrib, attrs, validators

from pygls.lsp import CompletionParams, CompletionList, CompletionItem, CompletionItemKind
from pygls.server import LanguageServer
from aac.parser import parse
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.definition_helpers import get_definitions_by_root_key
from aac.lang.definitions.definition import Definition

SPACE_TRIGGER = " "


@attrs
class CodeCompletionProvider:
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

    def handle_code_completion(self, ls: LanguageServer, params: CompletionParams):
        """Resolve the trigger to the corresponding code completion function, then execute it."""
        trigger_character = params.context.trigger_character

        if not trigger_character:
            source_document_content = _get_code_completion_parent_text_file(ls, params).split(os.linesep)
            trigger_character = source_document_content[params.position.line][params.position.character - 1]

        callback_function = self.completion_callbacks.get(trigger_character)
        if callback_function:
            return callback_function(ls, params)
        else:
            logging.debug(f"Failed to find corresponding code completion function for the registered trigger: {trigger_character} in registered callbacks: {self.completion_callbacks}")


def _handle_space_code_completion(ls: LanguageServer, params: CompletionParams):
    source_document_content = _get_code_completion_parent_text_file(ls, params).split(os.linesep)
    position_line = source_document_content[params.position.line]

    if position_line.strip().startswith("type:"):
        return _get_reference_completion_items(ls, params)


def _get_reference_completion_items(ls: LanguageServer, params: CompletionParams):
    active_context = get_active_context()
    primitives_definition = active_context.get_primitives_definition()

    primitive_references = {}
    if primitives_definition:
        primitive_references = {field: "Primitive type" for field in active_context.get_primitive_types()}

    data_definition_references = _convert_definitions_to_name_description_dictionary(active_context.get_definitions_by_root_key("data"))

    file_definitions = parse(_get_code_completion_parent_text_file(ls, params))
    file_data_references = _convert_definitions_to_name_description_dictionary(get_definitions_by_root_key("data", file_definitions))

    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(
                label=reference,
                kind=CompletionItemKind.Reference,
                documentation=""
            )
            for reference in primitive_references | data_definition_references | file_data_references
        ],
    )


def _get_code_completion_parent_text_file(ls: LanguageServer, params: CompletionParams):
    return ls.workspace.documents.get(params.text_document.uri).source


def _convert_definitions_to_name_description_dictionary(definitions: list[Definition]) -> dict:
    return {definition.name: definition.get_fields().get("description") or "" for definition in definitions}
