---
layout: default
title: Definition Extensions
parent: Advanced User Topics
permalink: docs/advanced_user_topics/definition_extensions
---

# Extensibility of AaC
One of our primary goals for AaC is that it be extensible enough to meet the needs of AaC's diverse user base. To this end, we have incorporated a mechanism for introducing additional information to `schema` and `enum` definitions into the AaC DSL. Allowing users to extend these two types of definitions allows users to extend the existing AaC DSL data structures, data types, and enumeration values.

We refer to the process of defining an extension to an AaC DSL definition as "extending the definition". In order to extend an AaC DSL definition, users need to create an `extension` definition. `extension` definitions allow users to specify a target definition to extend via the field `type`. Because the information that is needed to extend a `schema` definition is different from that needed to extend an `enum`, users must choose one of the two extension fields: `schemaExt` or `enumExt`. As the names indicate, if a user is extending a `schema` definition then they would include the `schemaExt` field, whereas if the user extending an `enum` definition then they would use the `enumExt` field. These two fields are mutually exclusive, and defining both in the same definition will result in validation errors.

# Extending a Schema
For AaC users who find that existing definitions are insufficient or that a `schema` definition would benefit from additional information, the AaC DSL provides a mechanism for extending `schema` definitions. After defining a new `extension` with the `schemaExt` field the two additional fields `add` and `required` are used to specify how the `schema` should be extended. Instances of `Field` that are defined in the extension's `add` field will be appended to the target definition. The field `required` is a list of field names that are required to be present. These fields allow users to add new fields to data structures (`schema` definitions), and specify additional required fields.

As an example, let's consider the first-party plugin `Gen-Protobuf` which adds an additional field `protobuf_message_options` to `schema` definitions. This additional field is used to allow users to specify [Protobuf Message Options](https://developers.google.com/protocol-buffers/docs/proto#options) in their modeled data structures (`schema` definitions) that are passed from the modeled message to the generated Protobuf message.

[Example gen_protobuf.yaml L45-L51](https://github.com/jondavid-black/AaC/blob/3dfc11baf0ec8d7250608bd16caebdae837fc8af/python/src/aac/plugins/first_party/gen_protobuf/gen_protobuf.yaml#L45-L51)
```yaml
ext:
   name: SchemaMessageOptions
   type: schema
   schemaExt:
      add:
        - name: protobuf_message_options
          type: KeyValuePair[]
```

As described previously, the extension `SchemaMessageOptions` is extending the `schema` definition with an additional field `protobuf_message_options`. So, the AaC DSL now supports defining schema definitions with the additional field like so:
```yaml
schema:
    name: MyMessage
    protobuf_message_options:
        - key: java_package
          value: com.example.foo
    fields:
        - name: exampleContent
          type: string
```

# Extending an Enum
The AaC DSL also supports extending `enum` values. These extensions can be used to add additional values to an enumeration. The first-party plugin `Gen-Protobuf` leverages an `enum` extension to add new primitive types that are supproted in Protobuf, but aren't present in the [core spec](https://github.com/jondavid-black/AaC/blob/main/python/src/aac/spec/spec.yaml).


[Example gen_protobuf.yaml new primitive types extension](https://github.com/jondavid-black/AaC/blob/main/python/src/aac/plugins/first_party/gen_protobuf/gen_protobuf.yaml#L26-L43)
```yaml
ext:
  name: ProtobufPrimitiveTypesExtension
  type: Primitives
  enumExt:
    add:
      - double
      - float
      - int32
      - int64
      - uint32
      - uint64
      - sint32
      - sint64
      - fixed32
      - fixed64
      - bool
      - string
      - bytes
```

With these new primitive types, users of the `Gen-Protobuf` plugin can model Protobuf-specific data structure fields. For instance, users can model inter-service messages like so:

```yaml
schema:
    name: MyMessage
    fields:
        - name: exampleContent
          type: string
        - name: dataValue
          type: fixed64
```
