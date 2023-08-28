# Model Definitions in AaC

The AaC `model` root key is used to represent the components of a system. These,
for example, can be the services in a system following a Microservice
Architecture (MSA) design.

In its most basic form, a `model` must have a `name` that distinguishes it from
other AaC definitions. At the same time, however, a `model` that defines nothing
more than a `name` is of little use for anything more than representing external
components or actors.

It is recommended to include some amount of `behavior` definitions for each
model as that allows users and the AaC package to understand the component as a
part of the system. Some questions we can answer for `model`s with defined
`behavior`s are:

1. What does the component do?
1. What inputs does it expect?
1. What outputs can other components expect from this component?

## Defining Systems Through Model Composition

Whether your system is a monolith or a collection of microservices, the `model`
root key is used to represent how components fit together as part of the system
and what those components do as part of the system.

To compose a system from individual `component`s, one uses the `components` key.

```yaml
model:
  name: AlarmClock
  description: A simple alarm clock
  components:
    - name: clock
      type: Clock
    - name: timer
      type: ClockTimer
    - name: alarm
      type: ClockAlarm
  behavior:
    - ...
```

### Defining System Behavior In Models

Each model should define one, or more, `behavior`s that describe the component's
behaviors. These behaviors include a descrpition of `input`s, `output`s, and
`scenario`s that show how the model interacts with different components in the
system.

Each `behavior` requires a `BehaviorType` which represents the method of
interaction for that behavior.

A `behavior` can also have any combination of `input`s and `output`s.

Additionally, the action of every behavior is represented by the `scenario`
structure. Each `scenario` describes necessary pre-conditions (`given`),
triggers (`when`), and post-conditions (`then`) for the behavior.

```yaml
model:
  name: AlarmClock
  description: A simple alarm clock
  components:
    - ...
  behavior:
    - name: setAlarm
      type: REQUEST_RESPONSE
      description: Set the alarm timer
      input:
        - name: targetTime
          type: Timestamp
      acceptance:
        - scenario: setTimer
          when:
            - The user sets the alarm timer
          then:
            - The alarm is triggered when the clock reaches the specified time
```

### Defining System State In Models

TBD
