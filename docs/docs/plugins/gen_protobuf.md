---
layout: default
title: Protobuf 3 Plugin
parent: AaC Plugins
nav_order: 2
---
# Generate Protobuf 3 Plugin
This plugin generates protobuf 3 messages from Architecture-as-Code models.

## Plugin Commands


### Generate Protobuf Messages
Shell command:

 `$ aac gen-protobuf`

Command arguments:

`-h, --help` - Shows a help message

`architecture_file` - The Architecture-as-Code file containing the root model you want to generate messages from.

`output_directory` - The directory to write the generated Protobuf messages to.

## Plugin Extensions & Definitions
In order to use this plugin, you'll have to extend your models to provide necessary contextual information for the protobuf generator.

Protobuf messages will only be generated for `schema:` definitions that are referenced in `model:behavior:` fields: `input:` and `output:`.

If you nest a `schema:` field in another `schema:` definition, then you do not need to set the `protobuf_type` attribute for the field since it will be ignored and a protobuf message will be generated for the nested data type and included into the generated protobuf messages.

### Enum - ProtobufFieldRepeat
A new enum has been added, `ProtobufFieldRepeat`, which provides a set of enum values that represent whether a field can have multiple (repeated) entries.

This enum is added as an extension to the `Fields` definition and is not a required field.

This new enum in `fields:` allows the user to define that the field is repeating. If the attribute `protobuf_repeat` is not set in a field definition, or the enum value is `not_repeated`, then the protobuf field will NOT be generated as a `repeated` field; only setting the `protobuf_repeat` attribute to `repeated` will cause the generated protobuf field to be marked as `repeated`

### Example Implementation
Before gen-protobuf plugin:
```yaml
schema:
  name: DataA
  fields:
  - name: msg
    type: string
---
schema:
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
schema:
  name: DataA
  fields:
  - name: msg
    type: string
    protobuf_type: string
---
schema:
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