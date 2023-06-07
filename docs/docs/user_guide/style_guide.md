---
layout: default
title: AaC Style Guide
parent: User's Guide to AaC
nav_order: 3
---

# The AaC Style Guide
This style guide documents a set of coding standards for the AaC Domain-specific language. This standard is applied to to Core Specification and first-party plugins. Users are not required to implement this style, but it is recommended that users leverage a consistent style and standard for their models. Consistency also reduces complexity for users as they don't have to manage the idiosyncrasies of different naming conventions for user libraries, or plugins.

# Declaring Multiple Definitions Per AaC File
The AaC DSL is based on YAML, and as such can not support multiple declarations of the same root key in the document. If users declare multiple definitions without the special YAML document token `---`, then AaC will be unable to correctly ingest those definitions in the AaC file.

Defining multiple definitions in the same file:

```yaml
model:
    name: SampleModel
---
enum:
    name: SampleEnum
    values:
        - ENUM_VALUE
```

Leaving out the separator will cause parsing errors and lacks visual breaks in definitions:

```yaml
model:
    name: SampleModel

enum:
    name: SampleEnum
    values:
        - ENUM_VALUE
```

# Naming Convention
Every entry in AaC is referred to as a definition, and definitions are the basic unit of modeling in AaC. Definitions are used to define data structures, enumeration types, models, and modeled system components. As such, they have several distinct conventions to give users a quick and low-effort way of distinguishing between the various parts of definitions such as their names used heavily in references, fields and attributes, enumeration values, and even core components such as root keys and primitive value types.


## Definition Fields and Attributes
Due to the self-defining nature of AaC, definitions are just compositions of fields and attributes defined by other `schema` definitions. In order to maintain a consistent experience for users, fields should be use camelCase for field names.

The following definitions follow the style of naming fields and attributes in camelCase.

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

Users leveraging the `ExampleInterfaceMessage` will have a data structure with fields such as `ExampleInterfaceMessage.msgMetaData` and `ExampleInterfaceMessage.msgData.msgContent`. Alternatively, if we don't follow the style for fields and attributes, our definitions might look like:

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

The resulting data structure `ExampleInterfaceMessage` will now have a structure with fields such as `ExampleInterfaceMessage.msg_Metadata` and `ExampleInterfaceMessage.MessageData.msg_content`. The inconsistent naming of fields can easily spiral into data structures and models that are hard to navigate or interact with.


## Definition Names
Because definition names are treated as unique identifiers they should adhere to PascalCase, also known as UpperCamelCase. Applying UpperCamelCase exclusively to defintion name's allows users to quickly distinguish a reference to a defintion (UpperCamelCase) from a reference to an attribute or field within a definition (camelCase). Due to AaC's heavy use of definition references, distinctly naming definition names as UpperCamelCase makes it clear to users that the referenced object is another definition.

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

If we didn't follow convention, the an example of an inconsistently styled model could look something like:

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

In the above example, a user unfamiliar with the project can easily be mislead into thinking that `simple_enum` is a primitive type.

## Enumeration Values
Enumeration values in AaC are all UPPSERCASE, following the common style for enumeration values and constants in programming languages such as Python and Java.

```yaml
enum:
    name: SampleEnums
    values:
     - VALUE_1
     - VALUE_2
     - VALUE_3
```

## Primitive Types
Primitive types in AaC are specifically the enumeration values in the `Primitives` definition as they respresent a uniquely special set of enumeration values that define the primitive types in AaC. Users who extend the primitive values should maintain the same style of snake_case and keep primitive type names succint names that are descriptive but short.


## Root Keys
Like the Primitive Types, the root keys in AaC are specifically defined in the definition `Root`. Additional root key can be defined by users via an extension to the `roots` definition.

Example root keys are `import`, `schema`, `model`, etc. If a one-word type isn't descriptive enough for your root key, keeping it succint and snake_case (e.g. `spring_boot_service`, `cloud_gateway`) is acceptable. Other style root keys will not conform to the standard employed by the Core Specification and first-party plugins, making it less obvious to users what the key is and it introduces higher probability of errors in user models.

# Organizing Imports
Each AaC file has a file-wide import declaration. This `import` declaration allows users to reference definitions provided via other user files and can be used to decompose large, complex models into multiple files.

Because `import` decalarations are file-wide, these clauses should be the first clause in AaC files. There is no logic that dictates the order of the entries in an AaC file, but maintaining the `import` clause as the first clause makes the file-wide dependencies immediately visible and instills readers with an immediate understanding of dependencies

An example file with an import clause at the top:

```yaml
import:
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

In larger AaC files, have the import clause not at the top of file can make it less obvious to users what other files and definitions the AaC file may rely on. Not only does it obfuscate file dependencies, it can increase the likelihood of users declaring another import clause elsewhere in the file.

# Decomposing Models Across Files
Users who have experience managing large code files will quickly recognize that large models can be difficult to manage in large AaC files. To this end, it's recommended that you distribute your models into logical, related groups in AaC files that are then imported by the other AaC files which rely on them. For instance, if you have a system model `ExampleSystemModel` with `schema` definitions defining internal data structures like inter-service messages or external API data structures, these `schema` definitions can be sequestered into a separate AaC file that solely contains these interface data structures. This file should be imported by the `ExampleSystemModel`, which references those interface data structures in its interactions and behaviors. Breaking models and their components by logical groups can also improve the navigation and organization of AaC projects.

The `import` keyword supports a list of relative or absolute paths to other user-defined files in the overall project. Users are not confined to a working directory or a single-flat directory for their AaC files. The files can be distributed in logical directories and subdirectories, or even alongside components in an existing software project.

It's recommended that your AaC file structure avoids circular imports (e.g. File A imports File B, File B imports File C, and File C imports File A). AaC has several checks to de-conflict circular imports, but circular imports may cause unexpected behavior and indicate poor project structure and organization.
