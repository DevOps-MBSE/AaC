# Schema Definitions in AaC

AaC employs a set of specialized definitions, all of which are defined with the root-level key `schema`, to establish data structures within the AaC Domain-Specific Language (DSL). These `schema`-defined data structures encompass various forms, such as internal and external message formats, inputs and outputs for modeled behaviors, custom structures for plugin developers or user libraries, and other essential data constructs needed for your team's modeling activities.

In the AaC DSL, every definition has its structure defined by a `schema` definition, which permits users to tailor the language to their team's requirements and even craft new DSLs or extensions within AaC.

Users can define these extensions locally in their user-defined AaC files, or they can leverage [plugins](../dev_guide/plugin_dev_guide.md) and [user libraries](./user_library.md) for common structures and functionalities shared across teams and repositories.

## Utilizing Schema Definitions

`Schema` definitions serve multiple roles in the AaC DSL. Some examples are provided below for common use cases: crafting message interfaces, custom data structures, and defining new definition instance types.

### Crafting Message Interfaces

Interface message structures provide structures for communication within your system or between system components. Using `schemas` one can define payloads exchanged with external systems, software applications, external actors, input for plugins, and intricate data inputs for validation purposes. Leveraging a `schema` definition as the `input` of a `model` definition's `behavior:input` or `behavior:output`, the `schema` acts as an interface message, documenting the data structure flowing into or out of a component within your modeled system. A useful way of documenting software application behavior inputs or outputs.

In our Alarm Clock model example, the `behavior` entry defines the input and behavior of our Alarm Clock model. The `behavior` contains an `input` named `Timestamp`, which is a `schema`-defined data structure representing information needed to set the alarm.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/alarm_clock.yaml
    :language: yaml
    :emphasize-lines: 17
    :lines: 6-28
```

The `Timestamp` `schema` definition below outlines the fields required to define an exact alarm time.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/structures.yaml
    :language: yaml
    :emphasize-lines: 2
    :lines: 12-28
```

While this example is simplified and not representative of a software system, the same approach applies to defining user requests, events from message queues, Swift XML messages in financial applications, or any other input/output data structure within your modeled system.

### Crafting Custom Data Structures

Given AaC's self-defining nature, users can employ the `schema` definition to craft their own data structures by using the `schema` root key. `Timestamp` serves as an example of a defined data structure with a `schema` root key that can be referenced by name, as demonstrated in the Alarm Clock model's `behavior`, or used as a component in more intricate data structures.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/structures.yaml
    :language: yaml
    :emphasize-lines: 2
    :lines: 12-28
```

#### Constructing Complex Data Structures via Composition

Each `schema` definition in AaC outlines a set of fields for the definition. These fields can be primitive types as per the AaC DSL, custom enum types, or references to other `schema` definitions. When a `schema` definition references other `schema` definitions within its field types, it assembles more intricate data structures through [composition](https://en.wikipedia.org/wiki/Object_composition). In our Alarm Clock model example, the definition `TimerAlert` references `Timestamp` as a field type.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/structures.yaml
    :language: yaml
    :emphasize-lines: 8
    :lines: 1-10
```

### Introducing New Definition Types

AaC permits users to define new instances of custom data structures. In our Alarm Clock example, you might want to model individual instances of `TimerAlert` with varying dates and alarm sounds. To do this, you extend the `Root` definition, where root keys in the AaC DSL are defined. The following extension example demonstrates how to expand the Root definition with a new field typed as the `TimerAlert` `schema` definition.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/structures.yaml
    :language: yaml
    :lines: 84-90
    :emphasize-lines: 6-7
```

With the new root key added, you can define instances of your custom data structure `TimerAlert` as shown below.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/structures.yaml
    :language: yaml
    :lines: 92-100
    :emphasize-lines: 1
```
