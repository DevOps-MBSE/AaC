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
        lexemes (list[Lexeme]): A list of lexemes for each item in the parsed definition.
        structure (dict): The dictionary representation of the definition.
    """

    name: str = attrib(validator=validators.instance_of(str))
    content: str = attrib(validator=validators.instance_of(str))
    lexemes: list[Lexeme] = attrib(default=Factory(list), validator=validators.instance_of(list))
    structure: dict = attrib(default=Factory(dict), validator=validators.instance_of(dict))

    def get_root_key(self) -> str:
        """Return the root key for the parsed definition."""
        return list(self.structure.keys())[0]

    def get_fields(self) -> dict[str, dict]:
        """Return a dictionary of the top-level fields that are populated in the defintion by field name to field dictionaries."""
        fields = self.structure.get(self.get_root_key())

        if not fields:
            logging.debug(f"Failed to find any fields defined in the definition. Definition:\n{self.structure}")
            fields = {}

        return fields

    def get_required(self) -> list[str]:
        """Return a list of field names if the definition has a required field."""
        fields = self.structure.get(self.get_root_key())
        required = []

        if "required" in fields:
            required = fields.get("required")

        return required

    def get_validations(self) -> list[dict]:
        """Return a list of validation entries dictionaries if the definition has a validation field or an empty list if not."""
        fields = self.structure.get(self.get_root_key())
        validation = []

        if "validation" in fields:
            validation = fields.get("validation")

        return validation

    def is_extension(self) -> bool:
        """Returns true if the definition is an extension definition."""
        return self.get_root_key() == "ext"

    def is_data_extension(self) -> bool:
        """Returns true if the definition is a data extension definition."""
        definition = self.structure.get("ext")
        return "dataExt" in definition and isinstance(definition["dataExt"], dict)

    def is_enum_extension(self) -> bool:
        """Returns true if the definition is an enum extension definition."""
        definition = self.structure.get("ext")
        return "enumExt" in definition and isinstance(definition["enumExt"], dict)

    def is_enum(self) -> bool:
        """Returns true if the definition is an enum definition."""
        return self.get_root_key() == "enum"

    def to_yaml(self) -> str:
        """Return a yaml string based on the current state of the definition including extensions."""
        return yaml.dump(self.structure, sort_keys=False)
