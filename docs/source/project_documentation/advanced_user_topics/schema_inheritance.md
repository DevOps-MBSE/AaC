---
layout: default
title: Modeling Data Structure Inheritance
parent: Advanced User Topics
permalink: project_documentation/advanced_user_topics/schema_inheritance
---

# Inheritance in AaC
Architecture-as-Code provides users with the ability to model inheritance in their data structures in a limited capacity. Inheritance can only be leveraged with `schema` definitions -- the definition used to define data structures.

In order to define inheritance in AaC, a `schema` definition must populate the field `inherits` with a list of names of other `schema` definitions. Those definitions referenced in the `inherits` field will provide the inheriting definition with transitive attributes consisting of the parent definitions' `fields` and `validation` entries.

## Example Usage
Schema definitions inherit `fields` and `validation` rules from their parent definitions. So, if you were to define a required field in the parent definition, it will also be required in the child definition.


In the example below, `DataA` has declared that it inherits `DataMessage`. Despite `DataeA` appearing to only have the field `request`, it has actually been extended with the fields and from `DataMessage` as it's ingested into the AaC DSL engine.

```{eval-rst}
.. literalinclude:: ../../../../python/model/flow/DataMessage.yaml
    :language: yaml
```

```{eval-rst}
.. literalinclude:: ../../../../python/model/flow/DataA.yaml
    :language: yaml
    :emphasize-lines: 6-7, 9-11
```

If we were to print out `DataA`'s structure after it's inheritance is applied, it would look like:
```yaml
schema:
  inherits:
    - DataMessage
  name: DataA
  fields:
    - name: request
      type: string
    - name: source            # <-- Inherited Field
      type: string            #
      description: The originator of the message.
    - name: destination       # <-- Inherited Field
      type: string            #
      description: The destination of the message.
    - name: content-length    # <-- Inherited Field
      type: int               #
      description: The length of the content of the message in bytes.
```

## Inheriting from Multiple Definitions
AaC supports modeling multiple inheritance. There is no functional difference between inheriting from one or multiple definitions other than there will be multiple sources that contribute transitive attributes.

