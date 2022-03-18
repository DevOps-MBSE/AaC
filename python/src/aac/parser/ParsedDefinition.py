""""""

from attr import Factory, attrib, attrs, validators

from aac.parser.Lexeme import Lexeme


@attrs
class ParsedDefinition:
    """A parsed Architecture-as-Code definition.

    Attributes:
        name (str): The name of the definition
        content (str): The textual representation of the definition.
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
