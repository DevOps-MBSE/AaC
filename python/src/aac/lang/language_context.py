"""The Language Context manages the highly-contextual AaC DSL."""

from attr import Factory, attrib, attrs, validators
from typing import Optional
import copy
import logging

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.search import search_definition
from aac.lang.definitions.type import is_array_type, remove_list_type_indicator
from aac.lang.definition_helpers import get_definitions_by_root_key


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
            target_definition_name = definition.get_top_level_fields().get("type")
            target_definition = self.get_definition_by_name(target_definition_name)
            if target_definition:
                _apply_extension_to_target_definition(target_definition, definition)
            else:
                logging.error(f"Extension failed to define target, field 'type' is missing. {definition.structure}")

    def add_definitions_to_context(self, definitions: list[Definition]):
        """
        Add the list of Definitions to the list of definitions in the LanguageContext, any extensions are added last.

        Args:
            definitions: The list of Definitions to add to the context.
        """
        extension_definitions = get_definitions_by_root_key("ext", definitions)
        extension_definition_names = [ext.name for ext in extension_definitions]
        non_extension_definitions = list(filter(lambda definition: definition.name not in extension_definition_names, definitions))

        for definition in non_extension_definitions:
            self.add_definition_to_context(definition)

        for extension_definitions in extension_definitions:
            self.add_definition_to_context(extension_definitions)

    def remove_definition_from_context(self, definition: Definition):
        """
        Remove the Definition from the list of definitions in the LanguageContext.

        Args:
            definition (Definition): The Definition to remove from the context.
        """
        if definition.name in self.definitions_name_dictionary:
            self.definitions_name_dictionary.pop(definition.name)

            if definition.is_extension():
                self._remove_extension_from_context(definition)
            else:
                self.definitions.remove(definition)

        else:
            definitions_in_context = self.get_defined_types()
            logging.error(
                f"Definition not present in context, can't be removed. '{definition.name}' not in '{definitions_in_context}'"
            )

    def remove_definitions_from_context(self, definitions: list[Definition]):
        """
        Remove the list of Definitions from the list of definitions in the LanguageContext, any extensions are removed last.

        Args:
            definitions (list[Definition]): The list of Definitions to remove from the context.
        """
        extension_definitions = get_definitions_by_root_key("ext", definitions)

        for definition in definitions:
            if definition not in extension_definitions:
                self.remove_definition_from_context(definition)

        for extension_definitions in extension_definitions:
            self.remove_definition_from_context(extension_definitions)

    def update_definition_in_context(self, definition: Definition):
        """
        Update the Definition in the list of definitions in the LanguageContext, if it exists.

        Args:
            definition (Definition): The Definition to update in the context.
        """

        if definition.name in self.definitions_name_dictionary:
            old_definition = self.definitions_name_dictionary.get(definition.name)

            if definition.is_extension():
                self._remove_extension_from_context(old_definition)
                self._apply_extension_to_context(definition)
            else:
                self.remove_definition_from_context(old_definition)
                self.add_definition_to_context(definition)
        else:
            definitions_in_context = self.get_defined_types()
            logging.error(
                f"Definition not present in context, can't be updated. '{definition.name}' not in '{definitions_in_context}'"
            )

    def update_definitions_in_context(self, definitions: list[Definition]):
        """
        Update the list of Definitions in the list of definitions in the LanguageContext, any extensions are added last.

        Args:
            definitions (list[Definition]): The list of Definitions to update in the context.
        """
        extension_definitions = get_definitions_by_root_key("ext", definitions)

        for definition in definitions:
            if definition not in extension_definitions:
                self.update_definition_in_context(definition)

        for extension_definitions in extension_definitions:
            self.update_definition_in_context(extension_definitions)

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
            return search_definition(root_definition, ["schema", "fields"])
        else:
            return []

    def get_primitives_definition(self) -> Optional[Definition]:
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

    def is_enum_type(self, type: str) -> bool:
        """
        Returns a boolean indicating if the type is defined and if it's defined as an enum.

        This method is helpful for discerning the type of a definition by its name. This is
        functionally equivalent to getting the definition by name from the context and then
        running the `Definition` method `is_enum()`

        Args:
            type (str): The enum's type string.

        Returns:
            A boolean indicating if the string matches an enum type defined in the context.
        """
        defintion = self.get_definition_by_name(type)

        is_enum_type = False
        if defintion:
            is_enum_type = defintion.is_enum()

        return is_enum_type

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

        definition_to_return = self.definitions_name_dictionary.get(definition_name)

        if not definition_to_return:
            logging.info(f"Failed to find the definition named '{definition_name}' in the context.")

        return definition_to_return

    def get_definitions_by_root_key(self, root_key: str) -> list[Definition]:
        """Return a subset of definitions with the given root key.

        Args:
            root_key (str): The root key to filter on.

        Returns:
            A list of definitions with the given root key.
        """

        def does_definition_root_match(definition: Definition) -> bool:
            return root_key == definition.get_root_key()

        return list(filter(does_definition_root_match, self.definitions))

    def get_definitions_by_file_uri(self, file_uri: str) -> list[Definition]:
        """Return a subset of definitions that are sourced from the target file URI.

        Args:
            file_uri (str): The source file URI to filter on.

        Returns:
            A list of definitions belonging to the target file.
        """

        def does_definition_source_uri_match(definition: Definition) -> bool:
            return file_uri == definition.source_uri

        return list(filter(does_definition_source_uri_match, self.definitions))


def _apply_extension_to_target_definition(target_definition_to_extend: Definition, extension_definition: Definition) -> None:
    """
    Apply the extension to the definitions it modifies.

    Args:
        target_definition_to_extend (Definition): The extension definition to extend.
        extension_definition (Definition): The extension definition to apply to the target definition.
    """
    extension_type = ""
    extension_field_name = ""
    if extension_definition.is_enum_extension():
        extension_type = "enum"
        extension_field_name = "values"
    else:
        extension_type = "schema"
        extension_field_name = "fields"

    ext_type = f"{extension_type}Ext"
    target_definition_fields_dict = target_definition_to_extend.get_top_level_fields()
    extension_definition_fields_dict = extension_definition.get_top_level_fields()
    extension_additional_values_dict = extension_definition_fields_dict.get(ext_type)

    original_field_values = target_definition_fields_dict.get(extension_field_name)
    if original_field_values is not None:
        updated_values = []
        new_values = extension_additional_values_dict.get("add") or []
        if extension_definition.is_enum_extension():
            updated_values = _get_extended_enum_values(original_field_values, new_values)
        else:
            updated_values = _get_extended_data_fields(original_field_values, new_values)

        target_definition_fields_dict[extension_field_name] = updated_values
    else:
        logging.error(
            f"Attempted to apply an extension to the incorrect target. Extension name '{extension_definition.name}' target definition '{target_definition_to_extend.name}'"
        )

    _add_extension_required_fields_to_defintion(target_definition_fields_dict, extension_additional_values_dict)


def _get_extended_enum_values(original_values: list, new_values: list) -> list:
    """Return a list of all unique original and new enum values combined together."""
    updated_values = {value: value for value in original_values}
    new_values = {value: value for value in new_values}
    updated_values.update(new_values)
    return list(updated_values.values())


def _get_extended_data_fields(original_fields: list, new_fields: list):
    """Return a list of all unique original and new data fields combined together."""
    updated_fields_dict = {value.get("name"): value for value in original_fields}
    unique_new_fields = list(filter(lambda field: field.get("name") not in updated_fields_dict.keys(), new_fields))
    new_fields_dict = {value.get("name"): value for value in unique_new_fields}
    updated_fields_dict.update(new_fields_dict)
    return list(updated_fields_dict.values())


def _add_extension_required_fields_to_defintion(target_definition_sub_dict, extension_dictionary_sub_dict):
    """Add the extension's additional required fields to the target definition."""
    if "required" in extension_dictionary_sub_dict:

        if "required" not in target_definition_sub_dict:
            target_definition_sub_dict["required"] = []

        target_definition_sub_dict["required"] += extension_dictionary_sub_dict.get("required") or []
