"""The Language Context manages the highly-contextual AaC DSL."""
import copy
import logging
from attr import Factory, attrib, attrs, validators
from collections import OrderedDict
from typing import Optional
from uuid import UUID

from aac.io.files.aac_file import AaCFile
from aac.lang.constants import (
    DEFINITION_FIELD_NAME,
    DEFINITION_FIELD_VALUES,
    DEFINITION_NAME_PRIMITIVES,
    DEFINITION_NAME_ROOT,
    ROOT_KEY_ENUM,
    ROOT_KEY_EXTENSION,
    ROOT_KEY_SCHEMA,
)
from aac.lang.definition_helpers import get_definitions_by_root_key
from aac.lang.definitions.definition import Definition
from aac.lang.definitions.extensions import apply_extension_to_definition, remove_extension_from_definition
from aac.lang.definitions.type import remove_list_type_indicator
from aac.lang.language_error import LanguageError
from aac.plugins.plugin import Plugin


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
        self.definitions_dictionary = {definition.uid: definition for definition in self.definitions}

    definitions: list[Definition] = attrib(default=Factory(list), validator=validators.instance_of(list))
    plugins: list[Plugin] = attrib(default=Factory(list), validator=validators.instance_of(list))

    # Private attribute - don't reference outside of this class.
    definitions_dictionary: dict[UUID, Definition] = attrib(
        init=False, default=Factory(dict), validator=validators.instance_of(dict)
    )

    def add_definition_to_context(self, definition: Definition):
        """
        Add the Definition to the list of definitions in the LanguageContext.

        Args:
            definition: The Definition to add to the context.
        """
        new_definition = copy.deepcopy(definition)

        if new_definition.uid not in self.definitions_dictionary:
            new_definition.source.is_loaded_in_context = True
            self.definitions_dictionary[new_definition.uid] = new_definition
            self.definitions.append(new_definition)
        else:
            logging.debug(
                f"Did not add definition '{new_definition.name}' to the context because one already exists with the same name."
            )

        if definition.is_extension():
            target_definition_name = definition.get_type()
            target_definition = self.get_definition_by_name(target_definition_name)

            definitions_with_target_definition_name = [
                definition for definition in self.definitions if target_definition.name == definition.name
            ]

            if len(definitions_with_target_definition_name) > 1:
                raise LanguageError(
                    f"Duplicate definitions found ({len(definitions_with_target_definition_name)}) with name '{target_definition_name}'."
                )
            elif target_definition:
                apply_extension_to_definition(definition, target_definition)
            else:
                logging.error(f"Extension failed to define target, field 'type' is missing. {definition.structure}")

    def add_definitions_to_context(self, definitions: list[Definition]):
        """
        Add the list of Definitions to the list of definitions in the LanguageContext, any extensions are added last.

        Args:
            definitions: The list of Definitions to add to the context.
        """

        def dirty_dependency_sort_for_definitions_with_inheritance(definitions: list[Definition]) -> list[Definition]:
            sorted_definitions: dict[str, Definition] = OrderedDict()

            for definition in definitions:
                sorted_definitions[definition.name] = definition

            for definition in definitions:
                inherited_definition_names = definition.get_inherits()
                for inherited_definition_name in inherited_definition_names:
                    if inherited_definition_name in sorted_definitions:
                        sorted_definitions.move_to_end(definition.name)

            return list(sorted_definitions.values())

        extension_definitions = get_definitions_by_root_key(ROOT_KEY_EXTENSION, definitions)
        extension_definition_names = [definition.name for definition in extension_definitions]

        schema_definitions = get_definitions_by_root_key(ROOT_KEY_SCHEMA, definitions)
        child_definitions = [definition for definition in schema_definitions if definition.get_inherits() is not None]
        sorted_child_definitions = dirty_dependency_sort_for_definitions_with_inheritance(child_definitions)
        child_definition_names = [definition.name for definition in child_definitions]
        secondary_definitions = child_definition_names + extension_definition_names

        initial_definitions = [definition for definition in definitions if definition.name not in secondary_definitions]

        for definition in initial_definitions:
            self.add_definition_to_context(definition)

        for definition in sorted_child_definitions:
            self.add_definition_to_context(definition)

        for extension_definition in extension_definitions:
            self.add_definition_to_context(extension_definition)

    def remove_definition_from_context(self, definition: Definition):
        """
        Remove the Definition from the list of definitions in the LanguageContext.

        Args:
            definition (Definition): The Definition to remove from the context.
        """
        if definition.uid in self.definitions_dictionary:
            definition.source.is_loaded_in_context = False
            self.definitions_dictionary.pop(definition.uid)
            self.definitions.remove(definition)
        else:
            definitions_in_context = self.get_defined_types()
            logging.error(
                f"Definition not present in context, can't be removed. '{definition.name}' not in '{definitions_in_context}'"
            )

        if definition.is_extension():
            target_definition_name = definition.get_type()
            target_definition = self.get_definition_by_name(target_definition_name)
            if target_definition:
                remove_extension_from_definition(definition, target_definition)
            else:
                logging.error(f"Extension failed to define target, field 'type' is missing. {definition.structure}")

    def remove_definitions_from_context(self, definitions: list[Definition]):
        """
        Remove the list of Definitions from the list of definitions in the LanguageContext, any extensions are removed last.

        Args:
            definitions (list[Definition]): The list of Definitions to remove from the context.
        """
        extension_definitions = get_definitions_by_root_key(ROOT_KEY_EXTENSION, definitions)
        extension_definition_names = [definition.name for definition in extension_definitions]
        non_extension_definitions = [
            definition for definition in definitions if definition.name not in extension_definition_names
        ]

        for definition in non_extension_definitions:
            if definition not in extension_definitions:
                self.remove_definition_from_context(definition)

        for extension_definition in extension_definitions:
            self.remove_definition_from_context(extension_definition)

    def update_definition_in_context(self, definition: Definition):
        """
        Update the Definition in the list of definitions in the LanguageContext, if it exists.

        Args:
            definition (Definition): The Definition to update in the context.
        """

        if definition.uid in self.definitions_dictionary:
            old_definition = self.definitions_dictionary.get(definition.uid)

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
        extension_definitions = get_definitions_by_root_key(ROOT_KEY_EXTENSION, definitions)
        extension_definition_names = [definition.name for definition in extension_definitions]
        non_extension_definitions = [
            definition for definition in definitions if definition.name not in extension_definition_names
        ]

        for definition in non_extension_definitions:
            if definition not in extension_definitions:
                self.update_definition_in_context(definition)

        for extension_definition in extension_definitions:
            self.update_definition_in_context(extension_definition)

    def get_root_keys(self) -> list[str]:
        """
        Get the list of root keys as defined in the LanguageContext.

        Returns:
            A list of strings, one entry for each root key in the LanguageContext.

            These keys may differ from those provided by the core spec since the LanguageContext applies definitions
            from active plugins and user files, which may extend the set of root keys.
            See :py:func:`aac.spec.get_root_keys()` for the list of root keys provided by the unaltered core AaC DSL.
        """
        return [field.get(DEFINITION_FIELD_NAME) for field in self.get_root_fields()]

    def get_root_fields(self) -> list[dict]:
        """
        Get the list of root fields as defined in the LanguageContext.

        Returns:
            A list of dictionaries, one dictionary for each root field including name and type.

            These fields may differ from those provided by the core spec since the LanguageContext applies definitions
            from active plugins and user files, which may extend the set of root fields.
        """
        return self.get_definition_by_name(DEFINITION_NAME_ROOT).get_fields()

    def get_root_keys_definition(self) -> Definition:
        """
        Return the root keys type definition in the LanguageContext.

        Returns:
            The definition that defines the root key types.

        Raises:
            LanguageError - An error indicating the root key definition is not in the context.
        """
        root_definition = self.get_definition_by_name(DEFINITION_NAME_ROOT)
        if root_definition:
            return root_definition
        else:
            missing_root_definition_error_message = (
                f"The root-key defining definition '{DEFINITION_NAME_ROOT}' is not in the context."
            )
            logging.critical(missing_root_definition_error_message)
            raise LanguageError(missing_root_definition_error_message)

    def get_primitives_definition(self) -> Definition:
        """
        Return the primitive type definition in the LanguageContext.

        Returns:
            The definition that defines the primitive types.

        Raises:
            LanguageError - An error indicating the primitive key definition is not in the context.
        """
        primitives_definition = self.get_definition_by_name(DEFINITION_NAME_PRIMITIVES)
        if primitives_definition:
            return primitives_definition
        else:
            missing_primitives_definition_error_message = (
                f"The AaC DSL primitive types defining definition '{DEFINITION_NAME_PRIMITIVES}' is not in the context."
            )
            logging.critical(missing_primitives_definition_error_message)
            raise LanguageError(missing_primitives_definition_error_message)

    def get_primitive_types(self) -> list[str]:
        """
        Get the list of primitive types as defined in the LanguageContext.

        Returns:
            A list of strings, one entry for each primitive type defined in the LanguageContext.

            These types may differ from those provided by the core spec since the LanguageContext applies definitions
            from active plugins and user files, which may extend the set of root keys.
            See :py:func:`aac.spec.get_primitives()` for the list of root keys provided by the unaltered core AaC DSL.
        """
        return self.get_primitives_definition().get_values()

    def get_defined_types(self) -> list[str]:
        """
        Return a list of strings containing the names of all the definitions in the LanguageContext.

        Returns:
            A list of strings, one entry for each definition name available in the LanguageContext.
        """
        return [definition.name for definition in self.definitions]

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
        definition = self.get_definition_by_name(type)
        return definition.is_enum() if definition else False

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
        definition_to_return = None
        if definition_name:
            definition_name = remove_list_type_indicator(definition_name)
            definition_to_return = [
                definition for definition in self.definitions_dictionary.values() if definition.name == definition_name
            ]

            if len(definition_to_return) > 0:
                if len(definition_to_return) > 1:
                    logging.info(
                        f"Multiple definitions found with the same name '{definition_name}' found in context. Returning the first"
                    )
                return definition_to_return[0]
            else:
                logging.info(f"Failed to find the definition named '{definition_name}' in the context.")
        else:
            logging.error(f"No definition name was provided to {self.get_definition_by_name.__name__}")

    def get_definitions_by_root_key(self, root_key: str) -> list[Definition]:
        """Return a subset of definitions with the given root key.

        Args:
            root_key (str): The root key to filter on.

        Returns:
            A list of definitions with the given root key.
        """
        return [definition for definition in self.definitions if root_key == definition.get_root_key()]

    def get_definitions_by_file_uri(self, file_uri: str) -> list[Definition]:
        """Return a subset of definitions that are sourced from the target file URI.

        Args:
            file_uri (str): The source file URI to filter on.

        Returns:
            A list of definitions belonging to the target file.
        """
        return [definition for definition in self.definitions if file_uri == definition.source.uri]

    def get_enum_definition_by_type(self, type: str) -> Optional[Definition]:
        """
        Return the enum definition that defines the specified enumerated type.

        Args:
            type (str): The type string.

        Returns:
            If the specified type is defined by an enum in the LanguageContext, returns the enum
            definition that defines the specified type. If not, returns None.
        """

        def is_type_defined_by_enum(enum: Definition) -> bool:
            return type in enum.get_top_level_fields().get(DEFINITION_FIELD_VALUES, [])

        enum_definitions = [enum for enum in self.get_definitions_by_root_key(ROOT_KEY_ENUM) if is_type_defined_by_enum(enum)]
        return enum_definitions[0] if enum_definitions else None

    def add_plugins(self, plugins: list[Plugin]):
        """Add the specified plugins to the current language context."""
        self.plugins.extend(plugins)

    def get_plugins(self) -> list[Plugin]:
        """
        Return the applied plugins that contribute to the current language context.

        Returns:
            The collection of applied plugins that contribute to the current language context.
        """
        return self.plugins

    def get_files_in_context(self) -> list[AaCFile]:
        """
        Return a list of all the files contributing definitions to the context.

        Returns:
            A list of all the files contributing definitions to the context.
        """
        return list({definition.source for definition in self.definitions})

    def get_file_in_context_by_uri(self, uri: str) -> Optional[AaCFile]:
        """
        Return the AaCFile object by uri from the context or None if the file isn't in the context.

        Args:
            uri (str): The string uri to search for

        Returns:
            An optional AaCFile if it's present in the context, otherwise None
        """
        for definition in self.definitions:
            if definition.source.uri == uri:
                return definition.source

        return None
