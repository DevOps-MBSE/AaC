"""The Language Context manages the highly-contextual AaC DSL."""

from typing import Optional
from attr import Factory, attrib, attrs, validators
import copy
import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.arrays import is_array_type, remove_list_type_indicator
from aac.lang.definitions.search import search_definition
from aac.lang.definition_helpers import (
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
        """Post init hook for attrs classes."""
        self.definitions_name_dictionary = {definition.name: definition for definition in self.definitions}

    definitions: list[Definition] = attrib(default=Factory(list), validator=validators.instance_of(list))

    # Private attribute - don't reference outside the class.
    definitions_name_dictionary: dict[str, Definition] = attrib(
        init=False, default=Factory(dict), validator=validators.instance_of(dict)
    )

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
            logging.debug(
                f"Did not add definition '{new_definition.name}' to the context because one already exists with the same name."
            )

        if definition.is_extension():
            self._apply_extension_to_context(definition)

    def add_definitions_to_context(self, definitions: list[Definition]):
        """
        Add the list of Definitions to the list of definitions in the LanguageContext, any extensions are added last.

        Args:
            definitions: The list of Definitions to add to the context.
        """
        extension_definitions = get_definitions_by_root_key("ext", definitions)

        for definition in definitions:
            if definition not in extension_definitions:
                self.add_definition_to_context(definition)

        for extension_definitions in extension_definitions:
            self.add_definition_to_context(extension_definitions)

    def get_root_keys(self) -> list[str]:
        """
        Get the list of root keys as defined in the LanguageContext.

        Returns:
            A list of strings, one entry for each root key in the LanguageContext.

            These keys may differ from those provided by the core spec since the LanguageContext applies definitions
            from active plugins and user files, which may extend the set of root keys.
            See :py:func:`aac.spec.get_root_keys()` for the list of root keys provided by the unaltered core AaC DSL.
        """
        return [field.get("name") for field in self.get_root_fields()]

    def get_root_fields(self) -> list[dict]:
        """
        Get the list of root fields as defined in the LanguageContext.

        Returns:
            A list of dictionaries, one dictionary for each root field including name and type.

            These fields may differ from those provided by the core spec since the LanguageContext applies definitions
            from active plugins and user files, which may extend the set of root fields.
        """
        root_definition = self.get_definition_by_name("root")

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
        return self.get_definition_by_name("Primitives")

    def get_primitive_types(self) -> list[str]:
        """
        Get the list of primitive types as defined in the LanguageContext.

        Returns:
            A list of strings, one entry for each primitive type defined in the LanguageContext.

            These types may differ from those provided by the core spec since the LanguageContext applies definitions
            from active plugins and user files, which may extend the set of root keys.
            See :py:func:`aac.spec.get_primitives()` for the list of root keys provided by the unaltered core AaC DSL.
        """
        return search_definition(self.get_primitives_definition(), ["enum", "values"])

    def get_defined_types(self) -> list[str]:
        """
        Return a list of strings containing the names of all the definitions in the LanguageContext.

        Returns:
            A list of strings, one entry for each definition name available in the LanguageContext.
        """
        return list(map(lambda definition: definition.name, self.definitions))

    def is_primitive_type(self, type: str) -> bool:
        """
        Returns a boolean indicating if the type is defined as a primitive type.

        Args:
            type (str): The type string.

        Returns:
            A boolean indicating if the string matches a primitive type defined in the context.
        """
        return remove_list_type_indicator(type) in self.get_primitive_types()

    def is_definition_type(self, type: str) -> bool:
        """
        Returns a boolean indicating if the type is defined by another definition.

        Args:
            type (str): The type string.

        Returns:
            A boolean indicating if the string matches a definition name within in the context.
        """
        return remove_list_type_indicator(type) in self.get_defined_types()

    def get_definition_by_name(self, definition_name: str) -> Optional[Definition]:
        """
        Return the definition corresponding to the argument, or None if not found.

        Args:
            definition_name (str): The definition name to search for.

        Returns:
            The definition corresponding to the name, or None if not found.
        """
        if is_array_type(definition_name):
            definition_name = remove_list_type_indicator(definition_name)

        return self.definitions_name_dictionary.get(definition_name)

    def _apply_extension_to_context(self, extension_definition: Definition) -> None:
        """
        Apply the extension to the definitions it modifies in the LanguageContext.

        Args:
            extension_definition (Definition): The extension definition to apply to the context.
        """
        target_to_extend = extension_definition.get_fields().get("type")

        if not target_to_extend:
            logging.error(f"Extension failed to define target, field 'type' is missing. {extension_definition.structure}")

        target_definition_to_extend = self.get_definition_by_name(target_to_extend)

        extension_type = ""
        extension_field_name = ""
        if extension_definition.is_enum_extension():
            extension_type = "enum"
            extension_field_name = "values"
        else:
            extension_type = "data"
            extension_field_name = "fields"

        ext_type = f"{extension_type}Ext"
        target_definition_extension_sub_dict = target_definition_to_extend.get_fields()
        extension_definition_fields = extension_definition.get_fields()

        extension_subtype_sub_dict = extension_definition_fields.get(ext_type)
        if target_definition_extension_sub_dict.get(extension_field_name):
            target_definition_extension_sub_dict[extension_field_name] += extension_subtype_sub_dict.get("add")
        else:
            logging.error(f"Attempted to apply an extension to the incorrect target. Extension name '{extension_definition.name}'")

        if "required" in extension_subtype_sub_dict:
            target_definition_extension_sub_dict["required"] += extension_subtype_sub_dict.get("required") or []
