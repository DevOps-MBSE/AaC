"""The Language Context manages the highly-contextual AaC DSL."""

from typing import Optional
from attr import Factory, attrib, attrs, validators
import copy
import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.arrays import is_array_type, remove_list_type_indicator
from aac.lang.definitions.search import search_definition
from aac.lang.definition_helpers import (
    get_definition_by_name,
    get_definitions_by_root_key,
)


@attrs(slots=True, auto_attribs=True)
class LanguageContext:
    """
    A management and utility class for the contextual AaC domain-specific language.

    Because the AaC DSL is self-defining, self-validating, and highly extensible, the DSL
    structure and rules are highly dependent on contextual definition sources such as active
    plugins, 3rd party definitions (libraries), and user-defined definitions.

    Attributes:
        definitions: The list of all definitions currently in the LanguageContext
    """
    def __attrs_post_init__(self):
        self.definitions_name_dictionary = {definition.name: definition for definition in self.definitions}

    definitions: list[Definition] = attrib(default=Factory(list), validator=validators.instance_of(list))

    # Private attribute - don't reference outside the class.
    definitions_name_dictionary: dict[str, Definition] = attrib(init=False, default=Factory(dict), validator=validators.instance_of(dict))

    def add_definition_to_context(self, definition: Definition):
        """
        Add the Definition to the list of definitions in the LanguageContext.

        Args:
            definition: The Definition to add to the context.
        """
        new_definition = copy.deepcopy(definition)

        if new_definition.name not in self.definitions_name_dictionary:
            self.definitions_name_dictionary[new_definition.name] = new_definition
            self.definitions.append(new_definition)
        else:
            logging.debug(f"Did not add definition '{new_definition.name}' to the context because one already exists with the same name.")

        if definition.is_extension():
            self._apply_extension_to_context(definition)

    def add_definitions_to_context(self, definitions: list[Definition]):
        """
        Add the list of Definitions to the list of definitions in the LanguageContext, any extensions are added last.

        Args:
            definitions: The list of Definitions to add to the context.
        """

        extension_definitions = get_definitions_by_root_key("ext", definitions)

        # Avoiding the use of sorted() since we already deepcopy each definition as we add it to the context.
        for definition in definitions:
            if definition not in extension_definitions:
                self.add_definition_to_context(definition)

        for extension_definitions in extension_definitions:
            self.add_definition_to_context(extension_definitions)

    def get_root_keys(self) -> list[str]:
        """
        Get the list of root keys as defined in the LanguageContext.

        Returns a list of strings indicating the current root keys in the active context. These
        keys may differ from those provided by the core spec since the LanguageContext applies definitions
        from active plugins and user files, which may extend the set of root keys.
        See :py:func:`aac.spec.get_root_keys()` for the list of root keys provided by the unaltered core AaC DSL.

        Returns:
            A list of strings, one entry for each root key in the LanguageContext.
        """
        def get_field_name(fields_entry_dict: dict):
            return fields_entry_dict.get("name")

        root_definition = get_definition_by_name("root", self.definitions)

        if root_definition:
            return list(map(get_field_name, search_definition(root_definition, ["data", "fields"])))
        else:
            return []

    def get_root_fields(self) -> list[dict]:
        """
        Get the list of root fields as defined in the LanguageContext.

        Returns a list of dictionaries that consist of the root fields in the active context. These
        keys may differ from those provided by the core spec since the LanguageContext applies definitions
        from active plugins and user files, which may extend the set of root keys.

        Returns:
            A list of dictionaries, one dictionary for each root field including name and type.
        """
        root_definition = get_definition_by_name("root", self.definitions)

        if root_definition:
            return search_definition(root_definition, ["data", "fields"])
        else:
            return []

    def get_primitives_definition(self) -> list[str]:
        """
        Return the primitive type definition in the LanguageContext.

        Returns:
            The definition that defines the primitive types.
        """
        return get_definition_by_name("Primitives", self.definitions)

    def get_primitive_types(self) -> list[str]:
        """
        Get the list of primitive types as defined in the LanguageContext.

        Returns a list of strings indicating the currently defined primitive types in the active context.
        These types may differ from those provided by the core spec since the LanguageContext applies definitions
        from active plugins and user files, which may extend the set of root keys.
        See :py:func:`aac.spec.get_primitives()` for the list of root keys provided by the unaltered core AaC DSL.

        Returns:
            A list of strings, one entry for each root name available in the LanguageContext.
        """
        return search_definition(self.get_primitives_definition(), ["enum", "values"])

    def get_defined_types(self) -> list[str]:
        """
        Get the list of types defined by other definitions in the LanguageContext.

        Returns a list of strings of all definition types in the active context.

        Returns:
            A list of strings, one entry for each definition name available in the LanguageContext.
        """
        return list(map(lambda definition: definition.name, self.definitions))

    def is_primitive_type(self, type: str) -> bool:
        """Returns a boolean indicating if the type is defined as a primitive type."""
        return remove_list_type_indicator(type) in self.get_primitive_types()

    def is_definition_type(self, type: str) -> bool:
        """Returns a boolean indicating if the type is defined by another definition."""
        return remove_list_type_indicator(type) in self.get_defined_types()

    def get_definition_by_name(self, definition_name: str) -> Optional[Definition]:
        """Return the definition corresponding to the argument, or None if not found."""
        if is_array_type(definition_name):
            definition_name = remove_list_type_indicator(definition_name)

        return self.definitions_name_dictionary.get(definition_name)

    def _apply_extension_to_context(self, extension_definition: Definition) -> None:
        """Apply the extension to the definitions it modifies in the LanguageContext."""
        target_to_extend = extension_definition.structure.get("ext").get("type")
        target_definition_to_extend = get_definition_by_name(target_to_extend, self.definitions)

        extension_type = ""
        extension_field_name = ""
        if extension_definition.is_enum_extension():
            extension_type = "enum"
            extension_field_name = "values"
        else:
            extension_type = "data"
            extension_field_name = "fields"

        ext_type = f"{extension_type}Ext"
        target_definition_dict = target_definition_to_extend.structure
        target_definition_extension_sub_dict = target_definition_dict.get(extension_type)
        extension_definition_fields = extension_definition.get_fields()

        extension_subtype_sub_dict = extension_definition_fields.get(ext_type)
        target_definition_extension_sub_dict[extension_field_name] += extension_subtype_sub_dict.get("add")

        if "required" in extension_subtype_sub_dict:
            target_definition_extension_sub_dict["required"] += extension_subtype_sub_dict.get("required") or []
