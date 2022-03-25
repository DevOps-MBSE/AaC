""""""

from attr import Factory, attrib, attrs, validators
import yaml

from aac.parser.Lexeme import Lexeme


@attrs
class ParsedDefinition:
    """A parsed Architecture-as-Code definition.

    Attributes:
        name (str): The name of the definition
        content (str): The original source textual representation of the definition.
        lexemes (list[Lexeme]): A list of lexemes for each item in the parsed definition.
        definition (dict): The parsed definition.
    """

    name: str = attrib(validator=validators.instance_of(str))
    content: str = attrib(validator=validators.instance_of(str))
    lexemes: list[Lexeme] = attrib(default=Factory(list), validator=validators.instance_of(list))
    definition: dict = attrib(default=Factory(list), validator=validators.instance_of(dict))

    def get_root_key(self) -> str:
        """Return the root key for the parsed definition"""
        return list(self.definition.keys())[0]

    def is_extension(self) -> bool:
        """Returns true if the definition is an extension definition."""
        return self.get_root_key() == "ext"

    def is_data_extension(self) -> bool:
        """Returns true if the definition is a data extension definition."""
        definition = self.definition.get("ext")
        return "dataExt" in definition and isinstance(definition["dataExt"], dict)

    def is_enum_extension(self) -> bool:
        """Returns true if the definition is an enum extension definition."""
        definition = self.definition.get("ext")
        return "enumExt" in definition and isinstance(definition["enumExt"], dict)

    def is_enum(self) -> bool:
        """Returns true if the definition is an enum definition."""
        return self.get_root_key() == "enum"

    def is_data(self) -> bool:
        """Returns true if the definition is a data definition."""
        return self.get_root_key() == "data"

    def to_yaml(self) -> str:
        """Return a yaml string based on the current state of the definition including extensions."""
        return yaml.dump(self.definition, sort_keys=False)
