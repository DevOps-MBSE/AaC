"""The Active Context maintains the highly-contextual AaC DSL."""
import copy
from attr import Factory, attrib, attrs, validators

from aac.parser import ParsedDefinition
from aac.lang.definition_helpers import (
    get_definition_by_name,
    get_definitions_by_root_key,
    search_definition,
    remove_list_type_indicator,
)


@attrs(slots=True, auto_attribs=True)
class ActiveContext:
    """
    A management and utility class for the contextual AaC domain-specific language.

    Because the AaC DSL is self-defining, self-validating, and highly extensible, the DSL
    structure and rules are highly dependent on contextual definition sources such as active
    plugins, 3rd party definitions (libraries), and user-defined definitions.

    Attributes:
        context_definitions: The list of all definitions currently in the ActiveContext
    """

    definitions: list[ParsedDefinition] = attrib(default=Factory(list), validator=validators.instance_of(list))

    def add_definition_to_context(self, parsed_definition: ParsedDefinition):
        """
        Add the ParsedDefinition to the list of definitions in the ActiveContext.

        Args:
            parsed_definition: The ParsedDefinition to add to the context.
        """
        self.definitions.append(copy.deepcopy(parsed_definition))

        if parsed_definition.is_extension():
            self._apply_extension_to_context(parsed_definition)

    def add_definitions_to_context(self, parsed_definitions: list[ParsedDefinition]):
        """
        Add the list of ParsedDefinitions to the list of definitions in the ActiveContext, any extensions are added last.

        Args:
            parsed_definitions: The list of ParsedDefinitions to add to the context.
        """

        extension_definitions = get_definitions_by_root_key("ext", parsed_definitions)

        # Avoiding the use of sorted() since we already deepcopy each definition as we add it to the context.
        for parsed_definition in parsed_definitions:
            if parsed_definition not in extension_definitions:
                self.add_definition_to_context(parsed_definition)

        for extension_definitions in extension_definitions:
            self.add_definition_to_context(extension_definitions)

    def get_root_keys(self) -> list[str]:
        """
        Get the list of root keys as defined in the ActiveContext.

        Returns a list of strings indicating the current root keys in the active context. These
        keys may differ from those provided by the core spec since the ActiveContext applies definitions
        from active plugins and user files, which may extend the set of root keys.
        See :py:func:`aac.spec.get_root_keys()` for the list of root keys provided by the unaltered core AaC DSL.

        Returns:
            A list of strings, one entry for each root name available in the ActiveContext.
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
        Get the list of root keys as defined in the ActiveContext.

        Returns a list of strings indicating the current root keys in the active context. These
        keys may differ from those provided by the core spec since the ActiveContext applies definitions
        from active plugins and user files, which may extend the set of root keys.

        Returns:
            A list of strings, one entry for each root name available in the ActiveContext.
        """
        root_definition = get_definition_by_name("root", self.definitions)

        if root_definition:
            return search_definition(root_definition, ["data", "fields"])
        else:
            return []

    def get_primitives_definition(self) -> list[str]:
        """
        Return the primitive type definition in the ActiveContext.

        Returns:
            The definition that defines the primitive types.
        """
        return get_definition_by_name("Primitives", self.definitions)

    def get_primitive_types(self) -> list[str]:
        """
        Get the list of primitive types as defined in the ActiveContext.

        Returns a list of strings indicating the currently defined primitive types in the active context.
        These types may differ from those provided by the core spec since the ActiveContext applies definitions
        from active plugins and user files, which may extend the set of root keys.
        See :py:func:`aac.spec.get_primitives()` for the list of root keys provided by the unaltered core AaC DSL.

        Returns:
            A list of strings, one entry for each root name available in the ActiveContext.
        """
        return search_definition(self.get_primitives_definition(), ["enum", "values"])

    def get_defined_types(self) -> list[str]:
        """
        Get the list of types defined by other definitions in the ActiveContext.

        Returns a list of strings of all definition types in the active context.

        Returns:
            A list of strings, one entry for each definition name available in the ActiveContext.
        """

        return list(map(lambda definition: definition.name, self.definitions))

    def is_primitive_type(self, type: str) -> bool:
        """Returns a boolean indicating if the type is defined as a primitive type."""
        return remove_list_type_indicator(type) in self.get_primitive_types()

    def is_definition_type(self, type: str) -> bool:
        """Returns a boolean indicating if the type is defined by another definition."""
        return remove_list_type_indicator(type) in self.get_defined_types()

    def _apply_extension_to_context(self, extension_definition: ParsedDefinition) -> None:
        """Apply the extension to the definitions it modifies in the ActiveContext."""
        target_to_extend = extension_definition.definition.get("ext").get("type")
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
        target_definition_dict = target_definition_to_extend.definition
        extension_definition_dict = extension_definition.definition

        extension_subtype_sub_dict = extension_definition_dict.get("ext").get(ext_type)
        target_definition_dict.get(extension_type)[extension_field_name] += extension_subtype_sub_dict.get("add")

        if "required" in extension_definition_dict["ext"][ext_type]:
            target_definition_dict.get(extension_type)["required"] += extension_subtype_sub_dict["required"]
