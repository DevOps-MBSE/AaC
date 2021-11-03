# Generate Protobuf Plugin
This plugin generates protobuf messages from Architecture-as-Code models.

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

Protobuf messages will only be generated for `data:` definitions that are referenced in `model:behavior:` fields: `input:` and `output:`.

If you nest a `data:` field in another `data:` definition, then you do not need to set the `protobuf_type` attribute for the field since it will be ignored and a protobuf message will be generated for the nested data type and included into the generated protobuf messages.

### Enum - ProtobufDataType
A new enum has been added, `ProtobufDataType`, which provides a new `fields:` attribute `protobuf_type`. This new enum in `fields:` provides typing information to the protobuf 3 generator needed to produce the correct types. If a `protobuf_type` is not provided, then the generator will simply insert the value in `type`. So, if you fail to specify the `protobuf_type` field as `protobuf_type: int64` then it would fallback to the value in `type: number`.

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
    type: string
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
    type: string
    protobuf_type: string
  required:
  - id_number
```

