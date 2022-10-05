---
layout: default
title: Modeling Data Structure Inheritance
parent: Advanced User Topics
permalink: docs/advanced_user_topics/schema_inheritance
---

# Inheritance in AaC
Architecture-as-Code provides users with the ability to model inheritance in their data structures in a limited capacity. Inheritance can only leveraged with `schema` definitions -- the definition used to define data structures.

In order to define inheritance in AaC, a `schema` definition must populate the field `inherits` with a list of names of other `schema` definitions. Those definitions referenced in the `inherits` field will provide the inheriting definition with transitive attributes consisting of the parent definitions' `fields` and `validations` entries.

## Example Usage
Schema definitions inherit fields and validation rules from their parent definitions. So, if you were to define a required field in the parent definition, it will also be required in the child definition.


In the example below, `InternalMessageA` has declared that it inherits `BaseMessage`. Despite `InternalMessageA` appearing to only have the field `some_data`, it has actually been extend with the fields and validations from `BaseMessage` as it's ingested into the AaC DSL engine.
```yaml
schema:
    name: BaseMessage
    fields:
        - name: source
          type: string
        - name: destination
          type: string
    validaton:
        - name: Required fields are present
          arguments:
            - source
            - destination
---
schema:
    name: InternalMessageA
    inherits:
        -
    fields:
        - name: some_data
          type: number
```

If we were to print out `InternalMessageA`'s structure after it's inheritance is applied, it would look like:
```yaml
schema:
    name: InternalMessageA
    inherits:
        -
    fields:
        - name: some_data
          type: number
        - name: source.     # <-- Inherited Field
          type: string.     #
        - name: destination # <-- Inherited Field
          type: string.     #
    validaton:
        - name: Required fields are present # <-- Inherited Validation
          arguments:
            - source
            - destination
```

## Inheriting from Multiple Definitions
AaC supports modeling multiple inheritance. There is no functional difference between inheriting from one or multiple definitions other than there will be multiple sources that contribute transitive attributes.

