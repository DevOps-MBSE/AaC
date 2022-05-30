---
layout: default
title: AaC Modeling Language Reference
parent: AaC User's Guide
nav_order: 2
---

# What is the Architecture-as-Code Domain-Specific Language?
Architecture-as-Code comes with a highly-specialized Domain-Specific Language (DSL) that enables the AaC language to be self-defining and self-validating. These attributes allow the AaC DSL to be highly extensible and customizable in order to support and address the needs of any team and the wide-range of stakeholders.

Architecture-as-Code's unique DSL allows teams to employ Model-Based Systems Engineering (MBSE) practices that seamlessly integrate with development teams. To meet this goal, AaC captures modeled systems in plain-text YAML syntax. Using plain-text YAML allows for easy integration with version-control software such as Git and leveraging GitOps practices.

### Definitions
At the core of the AaC language are the yaml entries that _define_ modeled systems, components, behaviors, interactions, and even elements of the AaC DSL itself -- hence the self-defining attribute of the language. Each of these entries is called a "definition". Each definition requires a root key to indicate to the AaC DSL, tooling, and the user, the expected structure of the YAML entry. **Definitions require unique names and are referenced by name.**

In the following example model, the first key `model` indicates that this yaml entry will have model-specific fields, such as `components` or `behavior`.
```yaml
model:
  name: ExampleModel
  description: A example model
  components:
    - name: component1
      type: ExampleComponent
    - name: component2
      type: ExampleComponent
  behavior:
    - name: Example Behavior
```

Unlike the `model` definition above which defines models and components of systems, the following `schema` definition is used to define a data structure.
```yaml
schema:
  name: TimeDataStructure
  fields:
    - name: Hours
      type: int
    - name: Minutes
      type: int
    - name: Seconds
      type: int
```

The two example aboves demonstrate the basic structure of the AaC language: each YAML entry/AaC definition starts with a defined root key which correlates to a registered schema.

### Root Keys
Because the AaC DSL is leveraging YAML, which is just a key-value mapping with loose schema, the AaC DSL must define the schema for each definition via root keys. The AaC DSL comes with several pre-defined root keys that you can use to define various aspects of your system.

The basic root keys can be located in the [base AaC DSL.](https://github.com/jondavid-black/AaC/blob/bbe61782720d5958e2794308d7fe397fc6398bd3/python/src/aac/spec/spec.yaml#L2-L67)

| Root Key | Description |
|----------|-------------|
| import | Used to reference other AaC DSL files and their definitions |
| enum | Used to define enumerated values and types |
| schema | Used to define data structures |
| model | Used to define a system, model, or component |
| usecase | Used to define usecases, or interactions between models |
| ext | Used to define extensions to `enum` or `schema` defintions |
| validation | Used to define validation rules for AaC definitions |


## Navigating the DSL
Because of the flexibility and extensibility of the AaC DSL, it may be difficult to understand how to look up the structures of the DSL or how to determine the expected structure of certain definitions. The AaC DSL has to primary components: the base-level DSL and context-based DSL contributions and extensions.

### The Base DSL (Core Spec)
Because the AaC DSL is self-defining and requires some foundational DSL structures, it has a special set of definitions that are always provided to the user, referred to as the "core specification" or "core spec".

The core spec can be found in the AaC Python package, or [here](https://github.com/jondavid-black/AaC/blob/main/python/src/aac/spec/spec.yaml).  The core spec defines a number of foundational aspects of the AaC DSL including which keys can be used as root keys and the structures of `schema`, `model`, `usecase`, `extension`, `validation`, and other basic language structures.

The core spec can also be retrieved from the AaC python package via the `print-spec` command.

### Extended DSL
In order to support a fully-extensible tool and DSL, the AaC DSL incorporates definitions from a number of contextual sources including user AaC files, shared/library AaC files, and plugins. When you run AaC commands such as `validate`, then the AaC package incorporates the superset of definitions from actively installed plugins, user-defined AaC files, and the core spec in order to create an extended DSL context. This is important because some plugins, such as the Generate Protobuf plugin, provides a set of [additional protobuf primitive types](https://github.com/jondavid-black/AaC/blob/bbe61782720d5958e2794308d7fe397fc6398bd3/python/src/aac/plugins/gen_protobuf/gen_protobuf.yaml#L26-L43) which allows users to define Protobuf-specific types for data structure fields.

The extended DSL, referred to as the active context, can be retrieved from the AaC python package via the `print-active-context` command. If you were to compare the output of the core spec and the active context commands it should be apparent how the AaC can be extended to suite the needs of various plugins/user-features and users.
