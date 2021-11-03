"""AaC Plugin implementation module for the aac-gen-protobuf plugin."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by the aac gen-plugin, and it won't be overwritten if the file already exists.
from iteration_utilities import flatten

from aac import parser, util
from aac.template_engine import (TemplateOutputFile, generate_template,
                                 load_templates,
                                 write_generated_templates_to_file)

plugin_version = "0.0.1"


def gen_protobuf(architecture_file: str, output_directory: str):
    """
    Generate protobuf messages from Arch-as-Code models.

    Args:
        architecture_file <str>: TODO add a helpful parameter description
        output_directory <str>: TODO add a helpful parameter description
    """
    parsed_models = parser.parse_file(architecture_file)

    loaded_templates = load_templates(__package__)

    data_messages = _collect_data_messages_from_behavior(parsed_models)
    message_template_properties = _generate_protobuf_template_details_from_data_message_models(data_messages)
    generated_template_messages = _generate_protobuf_messages(loaded_templates, message_template_properties)

    write_generated_templates_to_file(generated_template_messages, output_directory)
    print(f"Succesfully generated templates to directory: {output_directory}")


def _collect_data_messages_from_behavior(parsed_models: dict) -> dict[str, dict]:
    """

    Returns:
        A dict of data message type keys to data message parsed model values
    """
    def collect_nested_data_types(interface_data_message_types: list[str]):
        nested_data_types = []
        for message_type in interface_data_message_types:
            data_model = parsed_models[message_type]["data"]

            for field in data_model.get("fields"):
                field_type = field.get("type")
                if field_type in parsed_models:
                    nested_data_types.append(field_type)

        return list(set(nested_data_types))

    def collect_behaviors(model_with_behaviors):
        return util.search(model_with_behaviors, ["model", "behavior"])

    def convert_behavior_io_to_data_type(behavior_io_model):
        return behavior_io_model.get("type")

    def collect_data_message_types(behavior_model):
        inputs = behavior_model.get("input") or []
        outputs = behavior_model.get("output") or []
        return list(map(convert_behavior_io_to_data_type, inputs + outputs))

    model_definitions = util.get_models_by_type(parsed_models, "model")
    behaviors = list(flatten(map(collect_behaviors, model_definitions.values())))
    interface_data_message_types = list(set(flatten(map(collect_data_message_types, behaviors))))
    all_data_types_to_generate = interface_data_message_types + collect_nested_data_types(interface_data_message_types)

    return {data_message_type: parsed_models[data_message_type] for data_message_type in all_data_types_to_generate}


def _generate_protobuf_template_details_from_data_message_models(data_message_models: dict) -> list[dict]:
    """
    Generates a list of template properties dictionaries for each protobuf file to generate.
    """

    template_properties_list = []
    for data_message_model in data_message_models.values():
        message_model_data = data_message_model.get("data")

        message_name = message_model_data.get("name")
        fields = message_model_data.get("fields") or []
        required = message_model_data.get("required") or []

        message_fields = []
        message_imports = []
        for field in fields:
            proto_field_name = field.get("name")
            proto_field_type = None

            field_type = field.get("type")
            field_proto_type = field.get("protobuf_type")
            if field_type in data_message_models:
                proto_field_type = field_type

                # This is the last time we have access to the other message, calculate its future protobuf file name here
                message_to_import = data_message_models.get(field_type).get("data")
                message_imports.append(_convert_message_name_to_file_name(message_to_import.get("name")))

            else:
                proto_field_type = field_proto_type or field_type

            proto_field_optional = not (proto_field_name in required)
            message_fields.append({"name": proto_field_name, "type": proto_field_type, "optional": proto_field_optional})

        template_properties_list.append({
            "name": message_name,
            "fields": message_fields,
            "imports": message_imports
        })

    return template_properties_list


def _generate_protobuf_messages(protobuf_message_templates: list, properties: dict) -> list[TemplateOutputFile]:
    """
    Compiles templates and file information.

    File and general structure style will follow the google protobuf style which can be found at
        https://developers.google.com/protocol-buffers/docs/style

    Returns:
        list of template information dictionaries.
    """

    def generate_protobuf_message_from_template(properties) -> TemplateOutputFile:
        generated_template = generate_template(protobuf_template, properties)
        generated_template.file_name = _convert_message_name_to_file_name(properties.get("name"))
        generated_template.overwrite = True  # Protobuf files shouldn't be modified by the user, and so should always overwrite
        return generated_template

    # This plugin produces only protobuf messages and one message per file due to protobuf specifications
    protobuf_template = None
    if len(protobuf_message_templates) != 1:
        raise GenerateProtobufException(f"Unexpected number of templates loaded {len(protobuf_message_templates)}, \
                    expecting only protobuf message template. Loaded templates: {protobuf_message_templates}")
    else:
        protobuf_template = protobuf_message_templates[0]

    return list(map(generate_protobuf_message_from_template, properties))


def _convert_message_name_to_file_name(message_name: str) -> str:
    """
    Converts a `data:` definition's name into an opinionated and stylized protobuf 3 file name.

    File and general structure style will follow the google protobuf style which can be found at
        https://developers.google.com/protocol-buffers/docs/style

    Args:
        message_name: the name of a `data:` definition to convert to a protobuf file name

    Returns:
        A protobuf file name string
    """
    new_file_name = f"{message_name}.proto"
    new_file_name = new_file_name.replace("- ", "_")
    new_file_name = _convert_camel_case_to_snake_case(new_file_name)
    return new_file_name


def _convert_camel_case_to_snake_case(camel_case_str: str) -> str:
    """
    Converts a camelCase string to a snake_case string.
    """
    snake_case_str = camel_case_str[:1].lower()
    for char in camel_case_str[1:]:
        snake_case_str += (char, f"_{char.lower()}")[char.isupper()]
    return snake_case_str


class GenerateProtobufException(Exception):
    """Exceptions specifically concerning protobuf message generation."""

    pass
