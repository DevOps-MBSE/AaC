"""The LanguageContext is a singleton that holds the current state of the AaC language, including all definitions and plugin runners."""
from typing import Any, Type
from os.path import join, dirname
from aac.context.language_error import LanguageError
from aac.execute.plugin_manager import get_plugin_manager
from aac.execute.plugin_runner import PluginRunner
from aac.context.definition import Definition
from aac.in_out.parser._parse_source import parse
from aac.context.definition_parser import DefinitionParser

AAC_LANG_FILE_NAME = "../aac.aac"
AAC_LANG_FILE_PATH = join(dirname(__file__), AAC_LANG_FILE_NAME)


class LanguageContext(object):
    """A singleton class that holds the current state of the AaC language."""

    def __new__(cls):
        """Create a new instance of the LanguageContext singleton class."""
        if not hasattr(cls, "context_instance"):
            cls.context_instance = super(LanguageContext, cls).__new__(cls)
            cls.context_instance.definitions = set()
            cls.context_instance.fully_qualified_name_to_definition: dict[
                str, Definition
            ] = {}
            cls.context_instance.fully_qualified_name_to_class: dict[str, Any] = {}
            cls.context_instance.plugin_runners = {}

            # load and initialize the AaC language
            cls.context_instance.parse_and_load(AAC_LANG_FILE_PATH)

            # load plugins
            get_plugin_manager().hook.register_plugin()

        return cls.context_instance

    def get_aac_core_file_path(self) -> str:
        """Function to return the AaC language file path."""
        return AAC_LANG_FILE_PATH

    def get_aac_core_as_yaml(self) -> str:
        """Function to return the AaC language as a yaml string."""
        with open(AAC_LANG_FILE_PATH) as aac_file:
            return aac_file.read()

    def get_aac_core_definitions(self) -> list[Definition]:
        """Function to return the definitions for the AaC language."""
        return self.parse_and_load(AAC_LANG_FILE_PATH)

    def _get_aac_generated_class(self, name: str) -> Type:
        definitions = self.get_definitions_by_name(name)
        if len(definitions) != 1:
            raise LanguageError(
                f"_get_aac_generated_class unable to identify unique definition for name '{name}'.  Found: {[definition.name for definition in definitions]}",
                definitions[0].source.uri
            )

        aac_class = self.context_instance.fully_qualified_name_to_class[
            definitions[0].get_fully_qualified_name()
        ]
        if not aac_class:
            raise LanguageError(
                f"_get_aac_generated_class unable to identify generated class for name '{name}' with fully_qualified_name '{definitions[0].get_fully_qualified_name()}'",
                definitions[0].source.uri
            )

        return aac_class

    def is_aac_instance(self, obj: Any, name: str):
        """Function to determine if an object is an instance of an AaC class."""
        return isinstance(obj, self._get_aac_generated_class(name))

    def create_aac_object(self, aac_type_name: str, attributes: dict) -> Any:
        """Function to create a python instance of an AaC class and attributes."""
        definitions = self.get_definitions_by_name(aac_type_name)
        if len(definitions) != 1:
            raise LanguageError(
                f"Unable to identify unique definition for '{aac_type_name}'.  Found {[definition.name for definition in definitions]}",
                definitions[0].source.uri
            )
        aac_class = self._get_aac_generated_class(aac_type_name)
        result = aac_class()
        field_names = [field.name for field in definitions[0].instance.fields]
        for attribute_name, attribute_value in attributes.items():
            if attribute_name not in field_names:
                raise LanguageError(f"Found undefined field name '{attribute_name}'", definitions[0].source.uri)
            setattr(result, attribute_name, attribute_value)
        return result

    def create_aac_enum(self, aac_enum_name: str, value: str) -> Any:
        """Function to create a python instance of an AaC enum class and value."""
        definitions = self.get_definitions_by_name(aac_enum_name)
        if len(definitions) != 1:
            raise LanguageError(
                f"Unable to identify unique definition for '{aac_enum_name}'.  Found {[definition.name for definition in definitions]}",
                definitions[0].source.uri
            )
        aac_class = self._get_aac_generated_class(aac_enum_name)
        try:
            return getattr(aac_class, value)
        except ValueError:
            raise LanguageError(
                f"{value} is not a valid value for enum {aac_enum_name}",
                definitions[0].source.uri
            )

    def parse_and_load(self, arg: str) -> list[Definition]:
        """Convenience function that parses a file or string and loads the definitions into the context."""
        parsed_definitions = parse(arg)
        parser = DefinitionParser()

        return parser.load_definitions(self, parsed_definitions)

    def remove_definitions(self, definitions: list[Definition]) -> None:
        """Remove the given definitions from the context."""
        for definition in definitions:
            definition.source.is_loaded_in_context = False
            self.context_instance.definitions.remove(definition)
            del self.context_instance.fully_qualified_name_to_definition[
                f"{definition.package}.{definition.name}"
            ]

    def get_definitions(self) -> list[Definition]:
        """Get all the definitions."""
        return list(self.context_instance.fully_qualified_name_to_definition.values())

    def get_definitions_by_name(self, name: str) -> list[Definition]:
        """Get all the definitions with a given name."""
        result = []
        search_name = name
        if "." not in name:
            search_name = f".{name}"
        for definition in self.get_definitions():
            if definition.get_fully_qualified_name().endswith(search_name.replace(" ", "")):
                result.append(definition)
        return result

    def get_definitions_by_root(self, root_key: str) -> list[Definition]:
        """Get all the definitions with a given root key."""
        result = []
        for definition in self.get_definitions():
            if definition.get_root_key() == root_key:
                result.append(definition)
        return result

    def get_defining_schema_for_root(self, root_key: str) -> Definition:
        """Get the defining schema for a given root key."""
        for definition in self.get_definitions():
            if definition.get_root_key() == "schema":
                if definition.instance.root == root_key:
                    return definition
        raise LanguageError(message=f"Could not find defining schema for root key: {root_key}", location=None)

    def register_plugin_runner(self, runner: PluginRunner) -> None:
        """Register a plugin runner."""
        if runner.get_plugin_name() not in self.context_instance.plugin_runners:
            self.context_instance.plugin_runners[runner.get_plugin_name()] = runner
        else:
            print(f"Plugin {runner.get_plugin_name()} already registered.")

    def get_plugin_runners(self) -> list[PluginRunner]:
        """Get all the plugin runners."""
        return list(self.context_instance.plugin_runners.values())

    def get_primitives(self) -> list[Definition]:
        """Get all the primitive definitions."""
        return self.get_definitions_by_root("primitive")

    def get_python_type_from_primitive(self, primitive_name: str) -> str:
        """Get the python type from a primitive name."""
        primitives = self.get_definitions_by_name(primitive_name)
        if len(primitives) != 1:
            raise LanguageError(
                message=f"Could not find unique primitive type: {primitive_name} - discovered {[primitive.name for primitive in primitives]}",
                location=None
            )
        return primitives[0].instance.python_type

    def is_extension_of(self, check_me: Definition, package: str, name: str) -> bool:
        """Check to see if a given definition extends from a given package and name."""
        definitions_of_type = self.get_definitions_of_type(package, name)
        return check_me in definitions_of_type

    def _recurse_type_inheritance(self, check_me: Definition) -> list[Definition]:
        result = []
        if "extends" in list(vars(check_me.instance).keys()):
            for extension in check_me.instance.extends:
                ext_package = extension.package
                ext_name = extension.name
                parent_definition = (
                    self.context_instance.fully_qualified_name_to_definition[
                        f"{ext_package}.{ext_name}"
                    ]
                )
                result.append(parent_definition)
                result.extend(self._recurse_type_inheritance(parent_definition))
        return result

    def get_definitions_of_type(self, package: str, name: str) -> list[Definition]:
        """Search the language context to find definitions that match a given package and name."""
        result = []
        # first make sure we can find the definition that defines the type
        if (
            f"{package}.{name}"
            not in self.context_instance.fully_qualified_name_to_definition
        ):
            raise LanguageError(f"Could not find definition for {package}.{name}", None)
        # now get all the definitions that extend from the definition
        definition = self.context_instance.fully_qualified_name_to_definition[
            f"{package}.{name}"
        ]
        result.append(definition)
        # loop through all definitions and see if the type we care about is in it's inheritance tree
        for item in self.get_definitions():
            inheritance_types = self._recurse_type_inheritance(item)
            if f"{package}.{name}" in [
                f"{definition.package}.{definition.name}"
                for definition in inheritance_types
            ]:
                result.append(item)
        return result

    def _traverse_field_chain(
        self, structure_list: list, field_chain: list[str]
    ) -> list:
        current_structures = structure_list
        search_depth = len(field_chain)
        current_depth = 0
        values_found = []
        for field_name in field_chain:
            next_structures = []
            for structure in current_structures:
                if field_name in structure:
                    if isinstance(structure[field_name], list):
                        if current_depth == search_depth - 1:
                            values_found.extend(structure[field_name])
                        else:
                            next_structures.extend(structure[field_name])
                    else:
                        if (
                            current_depth == search_depth - 1
                        ):  # This just means we're at the end of the field chain and should pull the value
                            values_found.append(structure[field_name])
                        else:
                            next_structures.append(structure.get(field_name, []))
            current_structures = next_structures
            current_depth += 1

        return values_found

    def get_values_by_field_chain(self, search_term: str) -> list:
        """Find values from the language context using a dot notation field chain."""
        result: list = []
        root_key = search_term.split(".")[0]
        candidate_values = self.get_definitions_by_root(root_key)
        result = self._traverse_field_chain(
            [definition.structure for definition in candidate_values],
            search_term.split("."),
        )
        return result
