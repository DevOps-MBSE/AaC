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

`architecture_file` - The Architecture-as-Code file containing the root system definition for which you want to generate Protobuf messages.

`output_directory` - The directory to write the generated Protobuf messages to.

## Plugin Extensions & Definitions
In order to use this plugin, you'll have to extend your `model`s to provide necessary contextual information for the Protobuf generator to identify interfaces and data structures.

Protobuf messages will only be generated for data structures identified as interface messages between `model`s. This requires that the modeled systems and components include behaviors with defined inputs and outputs. `schema:` definitions that are referenced in `model:behavior:` fields: `input:` and `output:` are identified as interface messages. Any substructure or embedded `enum` in the interface messages will also be included in the generated Protobuf messages -- so you can nest `schema` definitions for complex user-defined messages.

# Protobuf 3 Features

Feature Implementation:

| Feature | Implementation Status |
|---------|-----------------------|
| [Scalar Values](#scalar-values) | ✅ Implemented |
| [User-defined Message Types](#user-defined-message-types) | ✅ Implemented |
| [Embedded Comments](#embedded-comments) | ✅ Implemented |
| [Reserved Fields](#reserved-fields) | ❌ Not Implemented |
| [Assigning Field Numbers](#assigning-field-numbers) | ❌ Not Implemented |
| [Enums](#enums) | ✅ Implemented |
| [Reserved Types](#reserved-types) | ❌ Not Implemented |
| [OneOf](#oneof) | ❌ Not Implemented |
| [Maps](#maps) | ❌ Not Implemented |
| [Packages](#packages) | ❌ Not Implemented |
| [Defining Services](#defining-services) | ❌ Not Implemented |
| [Options](#options) | ✅ Implemented |
| [Optional Keyword](#optional-keyword) | ❗️❌❗️ Won't Implement |


## Scalar Values
All primitive/scalar [Protobuf 3 value types](https://developers.google.com/protocol-buffers/docs/proto3#scalar) types are supported.
The full list can be found in the plugin's definition, [`ProtobufPrimitiveTypesExtension`](https://github.com/jondavid-black/AaC/blob/main/python/src/aac/plugins/gen_protobuf/gen_protobuf.yaml).

The scalar values are added to the `Primitives` defintion and can be used inline very easily.
```yaml
schema:
  name: SomeDataMessage
  fields:
    - name: some_data
      type: string # String is already defined as a type in the core AaC DSL
      description: Some description for some_data
    - name: some_numbers
      type: fixed64[] # The fixed64 type is supplied by this plugin
      description: A description for some_numbers
```

## User-defined Message Types
This plugin generates Protobuf [user-defined](https://developers.google.com/protocol-buffers/docs/proto3#adding_more_message_types) messages, one per file, for every non-primitive type referenced. For each `schema:` definition identified as an interface message, or a substructure of an interface messages, a user-defined message type is generated.

## Embedded Comments
This plugin leverages the `description` field in AaC models to generate corresponding [comments](https://developers.google.com/protocol-buffers/docs/proto3#adding_comments) in the Protobuf messages.

`schema:` and `enum:` definitions support generating comments for Protobuf messages by populating those definition's top-level `description` field.

Only `schema:` definitions allow for field/value level comments. These comments are populated by defining the `description` field in the `fields` entries of a `schema:` definition.

An example of embedding comments in the Protobuf message looks like:
```yaml
schema:
  name: SomeDataMessage
  description: |
    Some description about my data message.
  fields:
    - name: some_data
      type: string
      description: Some description for some_data
    - name: some_numbers
      type: fixed64[]
      description: A description for some_numbers
```

With the corresponding output:
```protobuf
syntax = "proto3"

/* Some description about my data message. */
message SomeDataMessage {

  /* Some description for some_data */
  string some_data = 1;

  /* A description for some_numbers */
  repeated fixed64 some_numbers = 2;
}
```

## Assigning Field Numbers
[assigning field numbers](https://developers.google.com/protocol-buffers/docs/proto3#assigning_field_numbers) isn't implemented yet. Field numbers are currently assigned by the field's position in the definition, starting at the first field being assigned the field number `1`.


## Reserved Fields
[Reserved Fields](https://developers.google.com/protocol-buffers/docs/proto3#reserved) aren't implemented yet.

## Enums
Protobuf [enums](https://developers.google.com/protocol-buffers/docs/proto3#enum) can easily be defined by defining AaC enums.

An example AaC enum definition would look like:
```yaml
enum:
  name: MessageType
  description: |
    Enums for the various supported message types.
  values:
    - type_1
    - type_2
    - type_3
```

The corresponding output will look like:
```protobuf
syntax = "proto3"

/* Enums for the various supported message types. */
enum MessageType {
  TYPE_1 = 1;
  TYPE_2 = 2;
  TYPE_3 = 3;
}
```

## Reserved Types
[Reserved Types](https://developers.google.com/protocol-buffers/docs/proto3#reserved_values) aren't implemented yet.

## OneOf
[OneOf](https://developers.google.com/protocol-buffers/docs/proto3#oneof) is not currently implemented

## Maps
Protobuf 3 [maps](https://developers.google.com/protocol-buffers/docs/proto3#maps) aren't currently implemented.


[Maps Backwards compatibility](https://developers.google.com/protocol-buffers/docs/proto3#backwards_compatibility)

## Packages
[Packages](https://developers.google.com/protocol-buffers/docs/proto3#packages) aren't implemented yet.

## Defining Services
[Defining Services](https://developers.google.com/protocol-buffers/docs/proto3#services) is not currently implemented.

## Options
Protobuf allows for special [options](https://developers.google.com/protocol-buffers/docs/proto3#options) that provide customization and context for the Protobuf tooling. Users can specify options for Protobuf messages by defining the field `protobuf_message_options` in `schema:` or `enum:`
definitions.

An example use of options would look like:
```yaml
schema:
  name: SomeDataMessage
  protobuf_message_options:
    - key: java_package
      value: "com.example.foo"
  fields:
    - name: some_data
      type: string
    - name: some_numbers
      type: fixed64[]
  validation:
    - name: Required fields are present
      arguments:
        - some_data
```

The corresponding output will look like:
```protobuf
syntax = "proto3"

option java_package = com.example.foo;

message SomeDataMessage {

  string some_data = 1;

  repeated fixed64 some_numbers = 2;
}
```

## Optional Keyword
Protobuf 3.15 implemented the `optional` keyword, however, the `optional` keyword is considered a anti-pattern in Protobuf 3 messages, because all fields are inherently optional in Protobuf 3 messages.

Because optional keywords are anti-patterns, and are used for VERY specific cases, we currently don't plan to implement the `optional` keyword for generated Protobuf 3 messages.