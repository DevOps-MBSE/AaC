# Model Definitions in AaC

The AaC `model` root key is used to represent the components of a system. These,
for example, can be the services in a system following a Microservice
Architecture (MSA) design.

In its most basic form, a `model` must have a `name` that distinguishes it from
other AaC definitions. At the same time, however, a `model` that defines nothing
more than a name should be treated as incomplete unless the intention is to
represent external components or actors.

It is recommended to include `behavior` definitions for each model to allow
users and the AaC package to understand the component as part of the system.
Some questions we can answer for `model`s with defined `behavior`s are:

1. What does the component do?
1. What inputs does it expect?
1. What outputs can the system or other components expect from this component?

## Defining Systems Through Model Composition

Whether your system is a monolith or a collection of microservices, the `model`
root key is used to represent how components fit together as part of the system
and what those components do as part of the system.

To compose a system from individual `component`s, one specifies additional
models in the system model's `components` field.

```{eval-rst}
.. literalinclude:: ../../../../python/features/alarm_clock/alarm_clock.yaml
    :language: yaml
    :lines: 6-38
    :emphasize-lines: 4-10
```

### Defining System Behavior In Models

Each model should define one, or more, `behavior`s that describe the component's
behaviors. These behaviors include a description of `input`s, `output`s, and
`scenario`s that show how the model interacts with different components in the


```{eval-rst}
.. literalinclude:: ../../../../python/features/alarm_clock/alarm_clock.yaml
    :language: yaml
    :lines: 6-38
    :emphasize-lines: 11-16
```

A `behavior` can also have any combination of `input`s and `output`s.

Additionally, the action of every behavior is represented by the `scenario`
structure. Each `scenario` describes necessary pre-conditions (`given`),
triggers (`when`), and post-conditions (`then`) for the behavior.

```{eval-rst}
.. literalinclude:: ../../../../python/features/alarm_clock/alarm_clock.yaml
    :language: yaml
    :lines: 6-38
    :emphasize-lines: 19, 21, 23, 25, 28, 30, 32
```
### External Models

An *External Model* is a `model` that does not include an *Acceptance Scenario*.  These types of models are used to create simplified interfaces representing external components or actors.  A typical use case for an External Model is to represent a user or external messenger that is not managed by AaC.  It allows you to quickly create models without having to fully implement them.

Bellow is an example External Model.

```{eval-rst}
.. literalinclude:: ../../../../python/features/alarm_clock/external.yaml
    :language: yaml
    :lines: 1-3
```
External Models can be referenced, created, and used the same as internal `model`s.

### Defining System State In Models

*Pending an accurate model representation and sufficient implementation of state
within models, this section will not be covered yet.*
