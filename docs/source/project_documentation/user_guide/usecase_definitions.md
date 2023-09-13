# Usecase Definitions in AaC

One of AaC's goals is to allow for a system to be modeled in a way that various disciplined users are able to understand and implement the model for their area of responsibility in the overall system. One of the system model aspects captured within AaC is the behavior of the system, which has a root key of `usecase`. The `usecase` describes a system behavior, who is involved with the system behavior, and outlines the steps for achieving the described system behavior.

## Utilizing Usecase Definitions

There is an example usecase within our alarm clock model example for setting the alarm time.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/usecase.yaml
    :language: yaml
    :lines: 6-24
```
By incorporating the `usecase`s for various system behaviors, the alarm clock is able to be evaluated for functional completeness that cannot be seen in the alarm clock model alone.

Some questions that come up when evaluating the system for functional completeness are outlined below. They can be addressed with the incorporation of a `usecase` definition for the system.

1. Does the system define the necessary participants?
2. Are all necessary functionalities feasible with the current system components?
3. Can the system be understood enough to be tested?

### Crafting Usecase Participants

The `participants` of the `usecase` are included as a portion of the `usecase` definition, highlighted below.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/usecase.yaml
    :language: yaml
    :emphasize-lines: 4-10
    :lines: 6-24
```

`participants` are actors (who) can perform the action on the system and what part(s) of the system are necessary for the action to be accomplished. Therefore we see three participants in the above example: `user`, `alarm`, and `timer`.

The `user` is the actor that wants to make a change in the alarm clock system.

The `alarm` is what the user wants to change within the alarm clock system.

The `timer` is for the alarm clock system to know when to trigger the `alarm`.

### Crafting Usecase Steps

The `steps` of the `usecase` are included as a portion of the `usecase` definition, highlighted below.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/usecase.yaml
    :language: yaml
    :emphasize-lines: 11-19
    :lines: 6-24
```

`steps` are actions that the system follows to accomplish the desired described behavior of the `usecase`. The number of steps varies based on how many interactions between the `participants` need to happen for the behavior to be accomplished. Each of the `steps` should involve only two `participants`. One participant (`source`) performing an `action` on another participant (`target`). Each action must be defined as a behavior in the `target`. For example, the model `AlarmClock` must have a behavior named `setAlarm` that can be invoked by the source `user`.

```{eval-rst}
.. literalinclude:: ../../../../python/model/alarm_clock/usecase.yaml
    :language: yaml
    :emphasize-lines: 3-5
    :lines: 16-20
```
