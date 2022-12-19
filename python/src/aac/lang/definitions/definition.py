"""An Architecture-as-Code definition augmented with metadata and helpful functions."""
from __future__ import annotations

import copy
import logging
import yaml

from attr import Factory, attrib, attrs, validators
from typing import Any, Optional
from uuid import UUID, uuid4

from aac.io.files.aac_file import AaCFile
from aac.lang.constants import (
    DEFINITION_FIELD_DESCRIPTION,
    DEFINITION_FIELD_EXTENSION_ENUM,
    DEFINITION_FIELD_EXTENSION_SCHEMA,
    DEFINITION_FIELD_FIELDS,
    DEFINITION_FIELD_INHERITS,
    DEFINITION_FIELD_TYPE,
    DEFINITION_FIELD_VALIDATION,
    DEFINITION_FIELD_VALUES,
    ROOT_KEY_ENUM,
    ROOT_KEY_EXTENSION,
    ROOT_KEY_SCHEMA,
)
from aac.lang.definitions.lexeme import Lexeme


@attrs(hash=False)
class Definition:
    """An Architecture-as-Code definition.

    Attributes:
        uid (UUID): A unique identifier for selecting the specific definition.
        name (str): The name of the definition
        content (str): The original source textual representation of the definition.
        source (AaCFile): The source document containing the definition.
        lexemes (list[Lexeme]): A list of lexemes for each item in the parsed definition.
        structure (dict): The dictionary representation of the definition.
    """

    uid: UUID = attrib(init=False, validator=validators.instance_of(UUID))
    name: str = attrib(validator=validators.instance_of(str))
    content: str = attrib(validator=validators.instance_of(str))
    source: AaCFile = attrib(validator=validators.instance_of(AaCFile))
    lexemes: list[Lexeme] = attrib(default=Factory(list), validator=validators.instance_of(list))
    structure: dict = attrib(default=Factory(dict), validator=validators.instance_of(dict))

    def __attrs_post_init__(self):
        """Post-init hook."""
        self.uid = uuid4()

    def __hash__(self) -> int:
        """Return the hash of this Definition."""
        return hash(self.name)

    def get_root_key(self) -> str:
        """Return the root key for the parsed definition."""
        return list(self.structure.keys())[0]

    # Get Field Functions

    def get_top_level_fields(self) -> dict[str, dict]:
        """
        Return a dictionary of the top-level fields that are populated in the definition where the key is the field name.

        Schema/data definitions will return their top-level fields, including a "fields" field. Because schema/data
        is self-defining, it may be easy to confuse the intention of this function and assume that it will returns the
        entries in a schema/data definition's `fields` field, which is not the case.

        The resulting structure is not a copy, but a reference to the Definition's underlying structure. Editing this
        data structure will alter the fields in the Definition.
        """
        fields = self.structure.get(self.get_root_key())

        if not fields:
            logging.debug(f"Failed to find any fields defined in the definition. Definition:\n{self.structure}")
            fields = {}

        return fields

    def get_description(self) -> Optional[str]:
        """Return the description for the current definition, or None if it isn't defined."""
        fields = self.get_top_level_fields()
        return fields.get(DEFINITION_FIELD_DESCRIPTION)

    def get_type(self) -> Optional[str]:
        """Return the string for the extension type field, or None if the field isn't defined."""
        fields = self.get_top_level_fields()
        return fields.get(DEFINITION_FIELD_TYPE)

    def get_validations(self) -> Optional[list[dict]]:
        """Return a list of validation entry dictionaries, or None if the field isn't defined."""
        fields = self.get_top_level_fields()
        return fields.get(DEFINITION_FIELD_VALIDATION)

    def get_inherits(self) -> Optional[list[str]]:
        """Return a list of Definition names that are inherited, or None if the field isn't defined."""
        fields = self.get_top_level_fields()
        return fields.get(DEFINITION_FIELD_INHERITS)

    def get_values(self) -> Optional[list[str]]:
        """Return a list of enum values, or None if there are no enum values defined."""
        fields = self.get_top_level_fields()
        return fields.get(DEFINITION_FIELD_VALUES)

    def get_fields(self) -> Optional[list[dict]]:
        """Return a list of field dictionaries, or None if there are no fields defined."""
        fields = self.get_top_level_fields()
        return fields.get(DEFINITION_FIELD_FIELDS)

    # Type Test Functions

    def is_extension(self) -> bool:
        """Returns true if the definition is an extension definition."""
        return self.get_root_key() == ROOT_KEY_EXTENSION

    def is_schema_extension(self) -> bool:
        """Returns true if the definition is a schema extension definition."""
        definition = self.get_top_level_fields()
        return DEFINITION_FIELD_EXTENSION_SCHEMA in definition and isinstance(
            definition[DEFINITION_FIELD_EXTENSION_SCHEMA], dict
        )

    def is_enum_extension(self) -> bool:
        """Returns true if the definition is an enum extension definition."""
        definition = self.get_top_level_fields()
        return DEFINITION_FIELD_EXTENSION_ENUM in definition and isinstance(definition[DEFINITION_FIELD_EXTENSION_ENUM], dict)

    def is_schema(self) -> bool:
        """Returns true if the definition is a schema definition."""
        return self.get_root_key() == ROOT_KEY_SCHEMA

    def is_enum(self) -> bool:
        """Returns true if the definition is an enum definition."""
        return self.get_root_key() == ROOT_KEY_ENUM

    # IO Functions

    def to_yaml(self) -> str:
        """Return a yaml string based on the current state of the definition including extensions."""
        return yaml.dump(self.structure, sort_keys=False)

    # Misc Functions

    def copy(self) -> Definition:
        """Return a deep copy of the definition."""
        return copy.deepcopy(self)

    def get_lexeme_with_value(
        self,
        search_value: Any,
        prefix_values: Optional[list[Any]] = None,
        suffix_values: Optional[list[Any]] = None,
    ) -> Optional[Lexeme]:
        """
        If it exists in definition, return the Lexeme whose value is specified by search_value.

        If provided, prefix_values and suffix_values will be searched before and after, respectively,
        the specific search_value. The order of elements in prefix_values and suffix_values is
        considered important for the purposes of this function.

        Args:
            self (Definition): The definition whose lexemes are being searched for search_value.
            search_value (Any): The value being searched.
            prefix_values (Optional[list[Any]]): An ordered list of values that should be found before search_value.
            suffix_values (Optional[list[Any]]): An ordered list of values that should be found after search_value.

        Returns:
            If a lexeme was found with the search_value, it is returned. Otherwise, None is returned.
        """
        prefix_values = prefix_values or []
        suffix_values = suffix_values or []
        values = [*prefix_values, search_value, *suffix_values]

        index = 0
        possible_match = None
        for lexeme in self.lexemes:
            found_all_values = len(values) == index

            if found_all_values:
                return possible_match
            elif lexeme.value == str(values[index]):
                if lexeme.value == str(search_value):
                    possible_match = lexeme
                index += 1
            else:
                index = 0

        return possible_match
