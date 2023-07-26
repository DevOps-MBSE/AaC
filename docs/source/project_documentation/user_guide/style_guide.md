---
layout: default
title: AaC Style Guide
parent: User's Guide to AaC
nav_order: 3
---

# The AaC Style Guide
This style guide documents a set of coding standards for the AaC Domain-Specific Language. This standard is implemented in the Core Specification and first-party plugins. Users are not required to implement this style, but it is recommended that users leverage a consistent style and standard for their models. Consistent styling reduces complexity and overhead for users as they don't have to manage the idiosyncrasies of different naming conventions for user libraries or plugins.

## Declaring Multiple Definitions Per AaC File
The AaC DSL is based on YAML, and as such, cannot support multiple declarations of the same root key in the YAML document (indicated by the special YAML document separator token `---`). If definitions are not separated by a document separator, then AaC will be unable to correctly ingest those definitions in the AaC file.

Correctly defining multiple definitions in the same file:

```yaml
model:
    name: SampleModel
---
model:
    name: AnotherModel
---
enum:
    name: SampleEnum
    values:
        - ENUM_VALUE
```

Incorrectly leaving out the separator will cause parsing errors and lacks visual breaks between definitions:

```yaml
model:
    name: SampleModel

model:
    name: AnotherModel

enum:
    name: SampleEnum
    values:
        - ENUM_VALUE
```

## Naming Convention
Every entry in AaC is referred to as a definition, and definitions are the basic unit of modeling in AaC. Definitions are used to define data structures, enumeration types, models, and modeled system components. As such, they have several distinct conventions to give users a quick and low-effort way of distinguishing between the various parts of definitions. These distinctions include definition names, fields and attributes, enumeration values, and even core language components such as root keys and primitive value types.


### Definition Fields and Attributes
Due to the self-defining nature of AaC, definitions are just instances and compositions of fields and attributes defined by other `schema` definitions.

In order to maintain a consistent experience for users interacting with these data structures, users should use `camelCase` for field names.

The following definitions follow the style of naming fields and attributes in `camelCase`.

```yaml
enum:
    name: ExampleSubStructure
    fields:
        - name: msgContent
          type: string
---
schema:
    name: ExampleInterfaceMessage
    fields:
        - name: msgMetadata
          type: string
        - name: msgData
          type: ExampleInterfaceMessage
```

Users leveraging the `ExampleInterfaceMessage` will have a data structure with fields such as `ExampleInterfaceMessage.msgMetaData` and `ExampleInterfaceMessage.msgData.msgContent`. Alternatively, if a user didn't follow the style for fields and attributes, our example definitions might look like:

```yaml
enum:
    name: ExampleSubStructure
    fields:
        - name: msg_content
          type: string
---
schema:
    name: ExampleInterfaceMessage
    fields:
        - name: msg_Metadata
          type: string
        - name: MessageData
          type: ExampleInterfaceMessage
```

The resulting data structure `ExampleInterfaceMessage` will now have an inconsistent naming convention in its structure with fields such as `ExampleInterfaceMessage.msg_Metadata` and `ExampleInterfaceMessage.MessageData.msg_content`. The inconsistent naming of fields can easily spiral into data structures and models that are hard to navigate or interact with for users and plugin developers.


### Definition Names
Because definition names are treated as unique identifiers they should adhere to `PascalCase`, also known as `UpperCamelCase`. Applying `UpperCamelCase` exclusively to definition name's allows users to quickly distinguish a reference to a definition (`UpperCamelCase`) from a reference to an attribute or field within a definition (`camelCase`). Due to AaC's heavy use of definition references, distinctly naming definition names as `UpperCamelCase` makes it clear to users that the referenced object is another definition.

Example reference of definitions by name:

```yaml
enum:
    name: SampleEnum
    values:
        - ENUM_VALUE
---
schema:
    name: ExampleDataStructure
    fields:
        - name: enumField
          type: SampleEnum
```

If a user didn't follow convention, an example of an inconsistently styled model could look something like:

```yaml
enum:
    name: sample_enum
    values:
        - ENUM_VALUE
---
schema:
    name: ExampleDataStructure
    fields:
        - name: enumField
          type: sample_enum
```

In this example, a user unfamiliar with the project can easily mistake `simple_enum` as a primitive type.

### Enumeration Values
Enumeration values in AaC are all `UPPERCASE`, following the common style for enumeration values and constants in programming languages such as Python and Java.

```yaml
enum:
    name: SampleEnums
    values:
     - VALUE_1
     - VALUE_2
     - VALUE_3
```

### Primitive Types
Primitive types in AaC are defined by the enumeration values in the `Primitives` definition. Each enum value represents a uniquely special set of enumeration values that define the core AaC language's primitive types. Users who extend `Primitives` should maintain the same style of `snake_case` and keep primitive type names succinct: in other words, names should be descriptive, but short.

### Root Keys
Like the primitive types, the available root keys in AaC are defined in the definition `Root`. Each field entry in the `Root` definition specifies the root key (the field's name) and a corresponding schema definition (the field type). Additional root keys can be defined by users via an extension to the `Root` definition.

Like primitive types, root keys should follow the `snake_case` style, but emphasize succinct, descriptive names. Example root keys are `import`, `schema`, `model`, etc. If a one-word type isn't descriptive enough for your root key, keeping it as succinct as possible (e.g. `spring_boot_service`, `cloud_gateway`) is preferable. Long-named root keys, or roots keys that aren't `snake_case`, will not conform to the standard employed by the Core Specification and first-party plugins and could introduce confusion about what the root key is.

## Organizing Imports
Each AaC file has a file-wide import declaration definition. Using an `import` definition allows users to reference definitions provided via other user files and can be used to decompose large, complex models into multiple files.

Because `import` declarations are file-wide, these clauses should be the first clause in AaC files. There is no internal logic that dictates the order of the entries in an AaC file, but maintaining the `import` clause as the first definition in AaC files makes the file-wide dependencies immediately visible and informs readers on the dependencies of file. Additionally, while it's possible to include multiple `import` definitions in a single file, the preferred approach is to list all imported files in a single `import` definition in each file.

An example file with an import clause at the top:

```yaml
import:
    files:
        - ../interface/service_a_messages.aac
---
model:
    name: ExampleService
    behavior:
        - name: ServiceBehavior
          type: request-response
          input:
            - name: userRequest
              type: ServiceARequestMessage
```

In larger AaC files, if an `import` definition is included, it should be placed at the top of file to make it obvious to users what other files and definitions the AaC file may rely on. If placed anywhere other than at the top of the file, not only are file dependencies obfuscated for readers, but the likelihood of users declaring another import definition elsewhere in the file increases.

## Decomposing Models Across Files
Users who have experience managing large code files will quickly recognize that large models can be difficult to manage in large AaC files. To this end, it's recommended that you distribute your models into logical, related groups in AaC files that are then imported by the AaC files that rely on them. For instance, if you have a system model `ExampleSystemModel` with `schema` definitions defining internal data structures like inter-service messages or external API data structures, these `schema` definitions can be sequestered into a separate AaC file that solely contains these interface data structures. This file should be imported by the `ExampleSystemModel`, which references those interface data structures in its interactions and behaviors. Breaking models and their components into related or logical groups can also improve the navigation and organization of AaC projects.

The `import` keyword supports a list of relative or absolute paths to other user-defined files in the overall project. Users are not confined to a working directory or a single-flat directory for their AaC files. The files can be distributed in directories and subdirectories, or even alongside their related components in existing software projects.

It's recommended that your AaC file structure avoids circular imports (e.g. File A imports File B, File B imports File C, and File C imports File A). AaC has some basic internal checks to de-conflict circular imports, but circular imports may cause unexpected behavior and indicate poor project organization.
