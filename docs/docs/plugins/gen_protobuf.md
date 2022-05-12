---
layout: default
title: Protobuf 3 Plugin
parent: AaC Plugins
nav_order: 2
---
# Generate Protobuf 3 Plugin
This plugin generates protobuf 3 messages from interface messages between Architecture-as-Code models.

## Plugin Commands


### Generate Protobuf Messages
Shell command:

 `$ aac gen-protobuf`

Command arguments:

`-h, --help` - Shows a help message

`architecture_file` - The Architecture-as-Code file containing the root system model that you want to generate messages for.

`output_directory` - The directory to write the generated Protobuf messages to.

## Plugin Extensions & Definitions
In order to use this plugin, you'll have to extend your models to provide necessary contextual information for the protobuf generator to identify interfaces and data structures.

Protobuf messages will only be generated for `data:` definitions that are referenced in `model:behavior:` fields: `input:` and `output:`.

If you nest a `data:` field in another `data:` definition, then you do not need to set the `protobuf_type` attribute for the field since it will be ignored and a protobuf message will be generated for the nested data type and included into the generated protobuf messages.

### Enum - ProtobufFieldRepeat
A new enum has been added, `ProtobufFieldRepeat`, which provides a set of enum values that represent whether a field can have multiple (repeated) entries.

This enum is added as an extension to the `Fields` definition and is not a required field.

This new enum in `fields:` allows the user to define that the field is repeating. If the attribute `protobuf_repeat` is not set in a field definition, or the enum value is `not_repeated`, then the protobuf field will NOT be generated as a `repeated` field; only setting the `protobuf_repeat` attribute to `repeated` will cause the generated protobuf field to be marked as `repeated`

### Example Implementation
Before gen-protobuf plugin:
```yaml
data:
  name: DataA
  fields:
  - name: msg
    type: string
---
data:
  name: DataB
  fields:
  - name: id_number
    type: number
  - name: code
    type: string[]
  required:
  - id_number
```

After gen-protobuf plugin:
```yaml
data:
  name: DataA
  fields:
  - name: msg
    type: string
    protobuf_type: string
---
data:
  name: DataB
  fields:
  - name: id_number
    type: number
    protobuf_type: int64
  - name: code
    type: string[]
    protobuf_type: string
  required:
  - id_number
```

# Implemented Protobuf 3 Features

## Scalar Values
All primitive/scalar [protobuf3 value types](https://developers.google.com/protocol-buffers/docs/proto3#scalar) are supported.
The full list can be found in the plugin's definition, `ProtobufPrimitiveTypesExtension`.

## User-defined Message Types
This plugin generates protobuf [user-defined](https://developers.google.com/protocol-buffers/docs/proto3#adding_more_message_types) messages, one per file, for every non-primitive type referenced. For each `schema:` definition identified as an interface message, or a substructure of an interface messages, a user-defined message type is generated.

## Embedded Comments
This plugin leverages the `description` field of models and fields to allow users to propagate comments into the protobuf messages.

<TODO example>

## Reserved Fields
[Reserved Fields](https://developers.google.com/protocol-buffers/docs/proto3#reserved)

## Enums
[Enums](https://developers.google.com/protocol-buffers/docs/proto3#enum)

## Reserved Types
[Reserved Types](https://developers.google.com/protocol-buffers/docs/proto3#reserved_values)

## OneOf
https://developers.google.com/protocol-buffers/docs/proto3#oneof

## Maps
https://developers.google.com/protocol-buffers/docs/proto3#maps

https://developers.google.com/protocol-buffers/docs/proto3#backwards_compatibility

## Packages
https://developers.google.com/protocol-buffers/docs/proto3#packages

## Defining Services
https://developers.google.com/protocol-buffers/docs/proto3#services

## Options
https://developers.google.com/protocol-buffers/docs/proto3#options