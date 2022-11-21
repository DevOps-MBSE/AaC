"""AaC Plugin implementation module for the aac-gen-protobuf plugin."""

import logging
import os
import re

from aac.lang.definitions.definition import Definition
from aac.lang.definitions.type import is_array_type, remove_list_type_indicator
from aac.lang.definitions.collections import get_definitions_by_root_key
from aac.lang.definitions.search import search_definition
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.language_context import LanguageContext
from aac.plugins import PluginError
from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result
from aac.templates.engine import TemplateOutputFile, generate_template, load_templates, write_generated_templates_to_file
from aac.validate import validated_source

plugin_name = "gen-protobuf"


def gen_protobuf(architecture_file: str, output_directory: str) -> PluginExecutionResult:
    """
    Gen-protobuf plugin command entry point. Generate protobuf messages from Arch-as-Code models.

    Args:
        architecture_file (str): The yaml file containing the data models to generate as Protobuf messages.
        output_directory (str): The directory to write the generated Protobuf messages to.
    """

    # Run our primary function, generate_protobuf, inside the plugin_result context manager
    with plugin_result(plugin_name, generate_protobuf_messages, architecture_file, output_directory) as result:
        return result


def generate_protobuf_messages(architecture_file: str, output_directory: str) -> None:
    """
    Generate protobuf messages from Arch-as-Code model interfaces.

    Args:
        architecture_file (str): The yaml file containing the data models to generate as Protobuf messages.
        output_directory (str): The directory to write the generated Protobuf messages to.
    """

    # Validate the source AaC file and its contents
    with validated_source(architecture_file) as validation_result:
        loaded_templates = load_templates(__package__, ".")

        # Get the validated model definitions
        validated_definitions = validation_result.definitions
        get_active_context().add_definitions_to_context(validated_definitions)
        model_definitions = get_definitions_by_root_key("model", validated_definitions)

        model_interface_messages = _get_model_interface_data_structures(model_definitions)
        protobuf_message_template_properties = _get_message_template_properties(model_interface_messages)

        generated_template_messages = _generate_protobuf_messages(
            loaded_templates,
            output_directory,
            protobuf_message_template_properties,
        )

        write_generated_templates_to_file(generated_template_messages)

        return f"Successfully generated templates to directory: {output_directory}"


def _get_model_interface_data_structures(model_definitions: list[Definition]) -> dict[str, Definition]:
    """
    Return a dict of definitions that are referenced as interface messages or as a nested type within an interface message.

    Model interface definitions are any definitions that are referenced as input or output for a model's behavior.

    Args:
        model_definitions (list[Definition]): A list of model definitions to parse for interface messages.

    Returns:
        A dict of data message type keys to data message parsed model values
    """
    interface_message_definitions = {}
    for model in model_definitions:
        interface_message_definitions.update(_get_model_behavior_input_output_definitions(model))

    active_context = get_active_context()

    all_message_definitions = {}
    all_message_definitions.update(interface_message_definitions)

    for message_definition in interface_message_definitions.values():
        if not message_definition.is_enum():
            message_sub_structures = _get_embedded_data_structures(message_definition, active_context)
            all_message_definitions.update(message_sub_structures)

    return all_message_definitions


def _get_model_behavior_input_output_definitions(model_definition: Definition) -> dict[str, Definition]:
    """Return a list of definitions that are defined in the input and output of model behavior's."""
    model_behavior_keys = ["model", "behavior"]

    model_interface_messages = []
    model_interface_messages += search_definition(model_definition, model_behavior_keys + ["input"])
    model_interface_messages += search_definition(model_definition, model_behavior_keys + ["output"])
    model_interface_message_names = [field.get("type") for field in model_interface_messages]

    active_context = get_active_context()
    interface_definitions = [active_context.get_definition_by_name(name) for name in model_interface_message_names]

    return {interface_def.name: interface_def for interface_def in interface_definitions}


def _get_embedded_data_structures(schema_definition: Definition, active_context: LanguageContext) -> dict[str, Definition]:
    """Return a dict of schema definition structures that make up the structure of the definition."""

    interface_message_substructures = {}
    definition_names_to_traverse = set([field.get("type") for field in schema_definition.get_top_level_fields().get("fields")])

    while len(definition_names_to_traverse) > 0:
        target_definition_name = definition_names_to_traverse.pop()
        target_definition = active_context.get_definition_by_name(target_definition_name)

        if target_definition:

            if target_definition.name not in interface_message_substructures:
                interface_message_substructures[target_definition.name] = target_definition

            if target_definition.is_schema():
                target_definition_field_types = [
                    field.get("type") for field in target_definition.get_top_level_fields().get("fields")
                ]

                # filter out already visited definitions
                filtered_target_field_types = list(
                    filter(lambda type: type not in interface_message_substructures, target_definition_field_types)
                )
                definition_names_to_traverse.update(filtered_target_field_types)

        else:
            logging.error(f"Failed to find definition for type '{target_definition_name}'")

    return interface_message_substructures


def _get_message_template_properties(interface_structures: dict[str, Definition]) -> list[dict]:
    """
    Analyzes data and enum models and produces a list of template property dictionaries for each protobuf file to generate.

    Args:
        data_and_enum_models: a dict of models where the key is the model name and the value is the model dict. Each model represents a protobuf message.

    Returns:
        a list of template property dicts
    """

    template_properties_list = []
    for definition in interface_structures.values():

        if definition.is_enum():
            template_properties_list.append(_get_enum_properties(definition))

        elif definition.is_schema():
            template_properties_list.append(_get_schema_properties(interface_structures, definition))

    return template_properties_list


def _to_template_properties_dict(
    name: str, description: str, enums: list[str] = [], fields: list[dict] = [], imports: list[str] = [], options: list = []
) -> dict[str, any]:
    """
    Return the template model properties dictionary for the provided arguments.

    Args:
        name (str): The name of the definition/message
        description (str): Optional description of the definition/message
        definition_type (str): The definition type
        enums (list): A list of enum values
        fields (list): A list of model fields
        imports (list): A list of model imports
        options (dict): A list of message options

    Returns:
        A dictionary containing the properties in a consistent structure.
    """
    active_context = get_active_context()
    file_type = "enum" if active_context.is_enum_type(name) else "schema"

    # Check if the value is a string, then format the string value it properly for protobuf.
    for option_entry in options:
        option_value = option_entry.get("value")

        if type(option_value) is str:
            option_entry["value"] = f'"{option_value}"'
        elif type(option_value) is bool:
            option_entry["value"] = str(option_value).lower()

    # Format the names
    name = _sanitize_string_to_pascal_case(name)

    # Format the enum values
    enums = [_sanitize_string_to_snake_case(enum).upper() for enum in enums]

    # Format the field strings
    for field in fields:
        field["name"] = _sanitize_string_to_snake_case(field.get("name"))
        if field["type"] not in active_context.get_primitive_types():
            field["type"] = _sanitize_string_to_pascal_case(field.get("type"))

    return {
        "message_name": name,
        "message_description": description,
        "file_type": file_type,
        "enums": enums,
        "fields": fields,
        "imports": imports,
        "options": options,
    }


def _get_enum_properties(enum_definition: Definition) -> dict[str, any]:
    """
    Analyzes an enum definition and returns a properties dictionary for template generation.

    Args:
        enum_definition (dict): An enum definition as a dictionary

    Returns:
         A dictionary containing the template generation properties.
    """
    enum_name = enum_definition.name
    enum_definition_fields = enum_definition.get_top_level_fields()
    enum_values = enum_definition_fields.get("values") or []
    enum_description = enum_definition_fields.get("description") or ""
    description_as_proto_comment = _convert_description_to_protobuf_comment(enum_description)
    definition_options = enum_definition_fields.get("protobuf_message_options") or []

    return _to_template_properties_dict(enum_name, description_as_proto_comment, enums=enum_values, options=definition_options)


def _get_schema_properties(interface_structures: dict[str, Definition], data_definition: Definition) -> dict[str, any]:
    """
    Analyzes a schema definition and returns a properties dictionary for template generation.

    Args:
        data_and_enum_models (dict): A list of data model and enum definitions for enum/data model reference lookup
        data_model (dict): A data model definition as a dictionary

    Returns:
         A dictionary containing the template generation properties.
    """
    active_context = get_active_context()
    definition_fields = data_definition.get_top_level_fields()
    structure_fields = definition_fields.get("fields")

    definition_name = data_definition.name
    definition_description = definition_fields.get("description") or ""
    definition_description_as_proto_comment = _convert_description_to_protobuf_comment(definition_description)
    definition_options = definition_fields.get("protobuf_message_options") or []

    message_fields = []
    message_imports = []
    for field in structure_fields:
        proto_field_name = field.get("name")
        proto_field_description = field.get("description") or ""
        proto_field_type = field.get("type")
        sanitized_proto_field_type = remove_list_type_indicator(proto_field_type)
        description_as_proto_comment = _convert_description_to_protobuf_comment(proto_field_description, 1)

        message_fields.append(
            {
                "name": proto_field_name,
                "description": description_as_proto_comment,
                "type": sanitized_proto_field_type,
                "repeat": is_array_type(proto_field_type),
            }
        )

        if sanitized_proto_field_type in interface_structures:
            definition_to_import = interface_structures.get(sanitized_proto_field_type)
            message_imports.append(_convert_message_name_to_file_name(definition_to_import.name))

        elif not active_context.is_primitive_type(sanitized_proto_field_type):
            bad_message_type = sanitized_proto_field_type
            identified_interface_types = list(interface_structures.keys())
            error_message = (
                f"Referenced message type '{bad_message_type}' isn't in the identified interface messages and data "
                f"structures: {identified_interface_types}."
            )
            logging.error(error_message)
            raise GenerateProtobufException(error_message)

    return _to_template_properties_dict(
        definition_name,
        definition_description_as_proto_comment,
        fields=message_fields,
        imports=message_imports,
        options=definition_options,
    )


def _generate_protobuf_messages(
    protobuf_message_templates: list, output_directory: str, properties: list[dict]
) -> list[TemplateOutputFile]:
    """
    Compile templates and with variable properties information.

    File and general structure style will follow the google protobuf style which can be found at
        https://developers.google.com/protocol-buffers/docs/style

    Args:
        protobuf_message_templates (list): Templates to generate against. (Should only be one template)
        properties (list[dict]): A list of dicts of properties

    Returns:
        List of template information dictionaries.
    """

    def generate_protobuf_message_from_template(properties) -> TemplateOutputFile:
        generated_template = generate_template(protobuf_template, output_directory, properties)
        generated_template.file_name = _convert_message_name_to_file_name(properties.get("message_name"))
        generated_template.overwrite = True  # Protobuf files shouldn't be modified by the user, and so should always overwrite
        return generated_template

    # This plugin produces only protobuf messages and one message per file due to protobuf specifications. (it only needs one template)
    protobuf_template = None
    if len(protobuf_message_templates) != 1:
        raise GenerateProtobufException(
            f"Unexpected number of templates loaded {len(protobuf_message_templates)}, "
            f"expecting only protobuf message template.\nLoaded templates: {protobuf_message_templates}"
        )
    else:
        protobuf_template = protobuf_message_templates[0]

    return list(map(generate_protobuf_message_from_template, properties))


def _convert_message_name_to_file_name(message_name: str) -> str:
    """
    Convert a `schema:` definition's name into an opinionated and stylized protobuf 3 file name.

    File and general structure style will follow the google protobuf style which can be found at
        https://developers.google.com/protocol-buffers/docs/style

    Args:
        message_name: the name of a `schema:` definition to convert to a protobuf file name

    Returns:
        A protobuf file name string
    """
    new_file_name = f"{message_name}.proto"
    new_file_name = new_file_name.replace("-", "_")
    new_file_name = new_file_name.replace(" ", "")
    new_file_name = _convert_camel_case_to_snake_case(new_file_name)
    return new_file_name


def _convert_camel_case_to_snake_case(camel_case_str: str) -> str:
    """
    Convert a camelCase string to a snake_case string.

    Args:
        camel_case_str: the camelCase string to convert

    Returns:
        a snake_case string
    """
    snake_case_str = camel_case_str[:1].lower()
    for char in camel_case_str[1:]:
        snake_case_str += (char, f"_{char.lower()}")[char.isupper()]
    return snake_case_str


def _sanitize_string_to_camel_case(string_to_convert: str) -> str:
    """
    Remove spaces from messages to convert them to CamelCaseStr.

    Args:
        message_with_space: the message containing a space to convert

    Returns:
        camelCaseStr
    """
    converted_string = ""
    change_to_camel = ""
    split_strings = re.findall(r"[A-Z][^A-Z]*|\s|-|_|;", string_to_convert)
    if len(split_strings) > 0:
        change_to_camel = "".join(string[0].upper() + string[1:].lower() for string in split_strings)
        converted_string = change_to_camel[0].lower() + change_to_camel[1:].replace(" ", "")
    else:
        converted_string = string_to_convert[0].lower() + string_to_convert[1:].replace(" ", "")

    return converted_string


def _sanitize_string_to_pascal_case(string_to_convert: str) -> str:
    """
    Remove spaces from messages to convert them to pascalCaseStr.

    Args:
        message_with_space: the message containing a space to convert

    Returns:
        PascalCaseStr
    """
    converted_string = ""
    change_to_pascal = ""
    split_strings = re.findall(r"[A-Z][^A-Z]*|\s|-|_|;", string_to_convert)
    if len(split_strings) > 0:
        change_to_pascal = "".join(string[0].upper() + string[1:].lower().replace("_", "") for string in split_strings)
        converted_string = change_to_pascal.replace(" ", "")
    else:
        converted_string = string_to_convert[0].upper() + string_to_convert[1:].replace(" ", "")

    return converted_string


def _sanitize_string_to_snake_case(string_to_convert: str) -> str:
    """
    Remove spaces from messages to convert them to snake_case_str.

    Args:
        message_with_space: the message containing a space to convert

    Returns:
        snake_case_str
    """
    converted_string = ""
    change_to_snake = ""
    split_on_space = re.split(r"\s|-|;", string_to_convert)
    if len(split_on_space) <= 1:
        converted_string = string_to_convert.lower()
    else:
        change_to_snake = "_".join(word.lower() for word in split_on_space)
        converted_string = change_to_snake

    return converted_string


def _convert_description_to_protobuf_comment(description: str, indent_level: int = 0) -> str:
    """
    Return the description as a protobuf multiline comment.

    The returned string is expected to slot into a template multitine comment like such:
        1. The first line isn't indented or starred
        2. every subsequent line break is indented and starred
    """
    space_indent = "  "
    additional_space_indent = space_indent * indent_level

    if description:
        formatted_multiline_comment = ""
        description_newlines = description.splitlines()

        formatted_multiline_comment = "/* "

        for i in range(0, len(description_newlines)):
            comment_line = description_newlines[i]

            comment_newline_value = os.linesep
            comment_line_prefix = f"{additional_space_indent} * "

            # if the first line in the description, don't add a line prefix
            if i == 0:
                comment_line_prefix = ""

            # if the final line in the description, don't add a line seperator
            if i == len(description_newlines) - 1:
                comment_newline_value = " */"

            formatted_multiline_comment += f"{comment_line_prefix}{comment_line}{comment_newline_value}"
    else:
        formatted_multiline_comment = ""

    return formatted_multiline_comment


class GenerateProtobufException(PluginError):
    """Exceptions specifically concerning protobuf message generation."""

    pass
