"""The Active Context maintains the highly-contextual AaC DSL"""

from attr import Factory, attrib, attrs, validators

from aac.parser import ParsedDefinition
from aac.definition_helpers import get_definition_by_name


@attrs(slots=True, auto_attribs=True)
class ActiveContext:
    """
    A class used to provide access to several disparate AaC model definition sources during the validation process.

    Attributes:
        core_aac_spec_model: A dict of the core AaC spec
        plugin_defined_definitions: a dict of definitions defined in the plugin's AaC file
        validation_target_models: a dict of models that are being validated.
    """

    active_context_definitions: list[ParsedDefinition] = attrib(default=Factory(list), validator=validators.instance_of(list))

    def add_definition_to_context(self, parsedDefinition: ParsedDefinition):
        """
        Add the ParsedDefinition to the list of definitions in the ActiveContext.

        Args:
            parsedDefinition: The ParsedDefinition to add to the context.
        """
        self.active_context_definitions.append(parsedDefinition)

        if parsedDefinition.is_extension():
            self._apply_extension_to_context(parsedDefinition)

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

        roots_model = self.get_all_extended_definitions().get("root")

        if roots_model:
            return map(get_field_name, roots_model.get("data").get("fields"))
        else:
            return []

    def _apply_extension_to_context(self, extension_definition) -> None:
        """Apply the extension to the definitions it modifies in the ActiveContext."""
        target_to_extend = extension_definition.definition.get("ext").get("type")
        target_definition_to_extend = get_definition_by_name(self.active_context_definitions, target_to_extend)

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

        # TODO: Tidy up
        extension_subtype_sub_dict = extension_definition_dict.get("ext").get(ext_type)
        target_definition_dict.get(extension_type)[extension_field_name] += extension_subtype_sub_dict.get("add")

        if "required" in extension_definition_dict["ext"][ext_type]:
            target_definition_dict.get(extension_type)["required"] += extension_subtype_sub_dict["required"]
