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
`models` in the system `model`'s `components` field.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/alarm_clock.yaml
    :language: yaml
    :lines: 6-37
    :emphasize-lines: 9-15
```

### Defining System Behavior In Models

Each model should define one, or more, `behavior`s that describe the component's
behaviors. These behaviors include a descrpition of `input`s, `output`s, and
`scenario`s that show how the model interacts with different components in the
system.

Each `behavior` requires a `BehaviorType` which represents the mode of
interaction for that behavior.

A `behavior` can also have any combination of `input`s and `output`s.

Additionally, the action of every behavior is represented by the `scenario`
structure. Each `scenario` describes necessary pre-conditions (`given`),
triggers (`when`), and post-conditions (`then`) for the behavior.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/alarm_clock.yaml
    :language: yaml
    :emphasize-lines: 23-37
    :lines: 6-37
```

### Defining System State In Models

*Pending an accurate model representation and sufficient implementation of state
within models, this section will not be covered yet.*
