from attr import Factory, attrib, attrs, validators
from uuid import UUID, uuid5, NAMESPACE_DNS

from aac.io.files.aac_file import AaCFile
from aac.lang.lexeme import Lexeme

@attrs(hash=False, eq=False)
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
