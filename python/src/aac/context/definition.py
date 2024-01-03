"""Definition class for Architecture-as-Code."""
from attr import Factory, attrib, attrs, validators
from typing import Any
from uuid import UUID, uuid5, NAMESPACE_DNS
import yaml

from aac.in_out.files.aac_file import AaCFile
from aac.context.lexeme import Lexeme
from aac.context.util import get_python_module_name, get_python_class_name, get_fully_qualified_name


@attrs(hash=False, eq=False)
class Definition:
    """An Architecture-as-Code definition.

    Attributes:
        uid (UUID): A unique identifier for selecting the specific definition.
        name (str): The name of the definition.
        package (str): The package of the definition.
        content (str): The original source textual representation of the definition.
        source (AaCFile): The source document containing the definition.
        lexemes (list[Lexeme]): A list of lexemes for each item in the parsed definition.
        structure (dict): The dictionary representation of the definition.
        instance (Any): A Python class instance of the definition.
    """

    uid: UUID = attrib(init=False, validator=validators.instance_of(UUID))
    name: str = attrib(validator=validators.instance_of(str))
    package: str = attrib(validator=validators.instance_of(str))
    content: str = attrib(validator=validators.instance_of(str))
    source: AaCFile = attrib(validator=validators.instance_of(AaCFile))
    lexemes: list[Lexeme] = attrib(default=Factory(list), validator=validators.instance_of(list))
    structure: dict = attrib(default=Factory(dict), validator=validators.instance_of(dict))
    instance: Any = attrib(default=None)

    def __attrs_post_init__(self):
        """Post-init hook."""
        self.uid = uuid5(NAMESPACE_DNS, str(self.__hash__()))
        if self.is_import():
            self.name = str(self.uid)

    def __hash__(self) -> int:
        """Return the hash of this Definition."""
        return hash(self.get_fully_qualified_name())

    def __eq__(self, obj):
        """Equals function for the Definition."""

        def is_equal() -> bool:
            equal = self.get_fully_qualified_name() == obj.get_fully_qualified_name()
            equal = equal and self.structure == obj.structure
            return equal

        return isinstance(obj, Definition) and is_equal()

    def get_root_key(self) -> str:
        """Get the root key for the definition.

        Returns:
            The root key for the definition.
        """
        return list(self.structure.keys())[0]

    def is_import(self) -> bool:
        """Return True if the definition is an import definition."""
        return self.get_root_key() == "import"

    def get_python_module_name(self) -> str:
        """Return the python module name for the definition."""
        if self.is_import():
            return ""
        return get_python_module_name(self.package)

    def get_python_class_name(self) -> str:
        """Return the python class name for the definition."""
        if self.is_import():
            return ""
        return get_python_class_name(self.name)

    def get_fully_qualified_name(self) -> str:
        """Return the fully qualified name of the definition."""
        if self.is_import():
            return ""
        # this is just the package and name joined with a dot
        return get_fully_qualified_name(self.package, self.name)

    def to_yaml(self) -> str:
        """Return a yaml string based on the current state of the definition including extensions."""
        return yaml.dump(self.structure, sort_keys=False)
