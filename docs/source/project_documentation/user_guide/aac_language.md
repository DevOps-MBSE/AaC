# What is the Architecture-as-Code Domain-Specific Language?
Architecture-as-Code comes with a highly-specialized Domain-Specific Language (DSL) that enables the AaC language to be self-defining and self-validating. These attributes allow the AaC DSL to be highly extensible and customizable in order to support and address the needs of any team and the wide-range of stakeholders.

Architecture-as-Code's DSL allows teams to employ Model-Based Systems Engineering (MBSE) practices that seamlessly integrate with development teams. To meet this goal, AaC captures modeled systems in plain-text YAML syntax. Using plain-text YAML allows for easy integration with version-control software such as Git and [leveraging GitOps practices.](./aac_gitops)

## Definitions
At the core of the AaC language are the yaml entries that _define_ modeled systems, components, behaviors, interactions, and even elements of the AaC DSL itself -- hence the self-defining attribute of the language. Each of these entries is called a "definition". Each definition requires a root key to indicate to the AaC DSL, tooling, and the user, the expected structure of the YAML entry. **Definitions require unique names and are referenced by name.**

In the following example model, the first key `model` indicates that this yaml entry will have model-specific fields, such as `components` and/or `behavior`.

```{eval-rst}
.. literalinclude:: ../../../../python/features/alarm_clock/alarm_clock.yaml
    :language: yaml
    :lines: 6-37
    :emphasize-lines: 1, 4, 11
```

Unlike the `model` definition above which defines models and components of systems, the following `schema` definition is used to define a data structure.
```{eval-rst}
.. literalinclude:: ../../../../python/features/alarm_clock/structures.yaml
    :language: yaml
    :lines: 14-29
    :emphasize-lines: 1
```

The two example aboves demonstrate the basic structure of the AaC language: each YAML entry/AaC definition starts with a defined root key which correlates to a registered schema that governs the YAML structure.

### DSL Root Keys
Because the AaC DSL is leveraging YAML, which is just a key-value mapping with loose schema, the AaC DSL must define the schema for each definition type via root keys. The AaC DSL comes with several pre-defined root keys that you can use to define various aspects of your system.

The basic root keys can be located in the [base AaC DSL definition](https://github.com/DevOps-MBSE/AaC/blob/main/python/src/aac.aac). These can be found in any definition containing a `root` field. Some of the root keys provided by the base DSL are:

| Root Key | Description |
|----------|-------------|
| import | Used to reference other AaC DSL files and their definitions |
| enum | Used to define enumerated values and types |
| schema | Used to define data structures |
| model | Used to define a system, model, or component |
| usecase | Used to define usecases, or interactions between models |
| plugin | Used to define plugins to provide AaC commands and constraints |


## Navigating the DSL
Because of the flexibility and extensibility of the AaC DSL, it may be difficult to understand how to look up the structures of the DSL or how to determine the expected structure of certain definitions. The AaC DSL has two primary components: the base-level DSL and the context-based DSL that is modified by contextual definitions and extension contributions coming from sources such as plugins or user libraries.

### The Base DSL (Core Definitions)
Because the AaC DSL is self-defining and requires some foundational DSL structures, it has a special set of definitions that are always provided to the user, referred to as the "core specification" or "core spec".

The core definitions can be found in the AaC Python package, or [here](https://github.com/DevOps-MBSE/AaC/blob/main/python/src/aac.aac).  The core definitions provide a number of foundational aspects of the AaC DSL including which keys can be used as root keys and the structures of `import`, `schema`, `model`, `usecase`, `enum`, `primitive`, `plugin` and other basic language structures.

The core definitions can also be retrieved from the AaC Python package via the `print-defs --core-only` command.

### Extended DSL
In order to support a fully extensible tool and DSL, the AaC DSL incorporates definitions from a number of contextual sources including user AaC files, shared/library AaC files, and plugins. When you run AaC commands such as `check`, the AaC package incorporates the superset of definitions from additionally installed plugins, user defined AaC files, and the core definitions in order to create an extended DSL context. This is important because some plugins may provide modifications which allow users to define structures differently.
