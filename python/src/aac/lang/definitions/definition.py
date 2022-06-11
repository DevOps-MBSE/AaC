"""An Architecture-as-Code definition augmented with metadata and helpful functions."""

from attr import Factory, attrib, attrs, validators
import logging
import yaml

from aac.lang.definitions.lexeme import Lexeme


@attrs
class Definition:
    """An Architecture-as-Code definition.

    Attributes:
        name (str): The name of the definition
        content (str): The original source textual representation of the definition.
        source_uri (str): The URI for the document containing the definition.
        lexemes (list[Lexeme]): A list of lexemes for each item in the parsed definition.
        structure (dict): The dictionary representation of the definition.
    """

    name: str = attrib(validator=validators.instance_of(str))
    content: str = attrib(validator=validators.instance_of(str))
    source_uri: str = attrib(validator=validators.instance_of(str))
    lexemes: list[Lexeme] = attrib(default=Factory(list), validator=validators.instance_of(list))
    structure: dict = attrib(default=Factory(dict), validator=validators.instance_of(dict))

    def get_root_key(self) -> str:
        """Return the root key for the parsed definition."""
        return list(self.structure.keys())[0]

    def get_top_level_fields(self) -> dict[str, dict]:
        """
        Return a dictionary of the top-level fields that are populated in the definition where the key is the field name.

        Schema/data definitions will return their top-level fields, including a "fields" field. Because schema/data
        is self-defining, it may be easy to confuse the intention of this function and assume that it will returns the
        entries in a schema/data definition's `fields` field, which is not the case.
        """
        fields = self.structure.get(self.get_root_key())

        if not fields:
            logging.debug(f"Failed to find any fields defined in the definition. Definition:\n{self.structure}")
            fields = {}

        return fields

    def get_required(self) -> list[str]:
        """Return a list of field names if the definition has a required field."""
        fields = self.get_top_level_fields()
        return fields.get("required") or []

    def get_validations(self) -> list[dict]:
        """Return a list of validation entry dictionaries if the definition has a validation field or an empty list if not."""
        fields = self.get_top_level_fields()
        return fields.get("validation") or []

    def is_extension(self) -> bool:
        """Returns true if the definition is an extension definition."""
        return self.get_root_key() == "ext"

    def is_schema_extension(self) -> bool:
        """Returns true if the definition is a schema extension definition."""
        definition = self.get_top_level_fields()
        return "schemaExt" in definition and isinstance(definition["schemaExt"], dict)

    def is_enum_extension(self) -> bool:
        """Returns true if the definition is an enum extension definition."""
        definition = self.get_top_level_fields()
        return "enumExt" in definition and isinstance(definition["enumExt"], dict)

    def is_schema(self) -> bool:
        """Returns true if the definition is a schema definition."""
        return self.get_root_key() == "schema"

    def is_enum(self) -> bool:
        """Returns true if the definition is an enum definition."""
        return self.get_root_key() == "enum"

    def to_yaml(self) -> str:
        """Return a yaml string based on the current state of the definition including extensions."""
        return yaml.dump(self.structure, sort_keys=False)
