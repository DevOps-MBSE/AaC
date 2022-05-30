---
layout: default
title: Decomposing Systems and Models in AaC
parent: AaC User's Guide
nav_order: 4
---
# 4. Defining Data Structure
## Defining Simple Data Structures
Defining data structures in AaC is fairly simple; any definition that starts with the key `schema` defines a data structure.

```yaml
schema:
    name: TimeDataStructure
    description: An example data structure for storing a timestamp consisting of hours, minutes, and seconds.
    - name: hours
      type: int
    - name: minutes
      type: int
    - name: seconds
      type: int
```

In the above example we have declared a data structure called `TimeDataStructure` with the fields, `TimeDataStructure.hours`, `TimeDataStructure.minutes`, and `TimeDataStructure.seconds`.

## Defining Complex Data Structures
In the event that you need to define a more complex data structure, perhaps one with nested data structures, you can do so by referencing other data structures as the type of a field. For instance, the following definition has a field, `timestamp` that is using the previously defined data structure `TimeDataStructure` as a field type.
```yaml
schema:
    name: TimezoneAwareTimeStamp
    - name: timestamp
      type: TimeDataStructure
    - name: timezoneOffset
      type: int
```

## Defining Data Structures for the AaC DSL
These data structures can also be used to define aspects of the AaC DSL. For example, the `schema` definition is used to [define its own structure.](https://github.com/jondavid-black/AaC/blob/bbe61782720d5958e2794308d7fe397fc6398bd3/python/src/aac/spec/spec.yaml#L277-L296)
```yaml
schema:
  name: schema
  fields:
    - name: name
      type: string
      description: |
        The name of the schema definition.
    - name: fields
      type: Field[]
      description: |
        A list of fields that make up the definition.
    - name: required
      type: string[]
      description: |
        The list of names of all the fields that are required for the
        definition.
    - name: validation
      type: ValidationReference[]
      description: |
        References and additional arguments for validations to apply to the definition.
```

In the definition above you can see that the fields `name`, `fields`, `required`, and `validation` are defined as top-level fields of the data structure named `schema`. That might be a little confusing at first, but if we take a look at the [defined structure](https://github.com/jondavid-black/AaC/blob/bbe61782720d5958e2794308d7fe397fc6398bd3/python/src/aac/spec/spec.yaml#L344-L370) for `model` definitions, then we'll see the top-level fields for the `model` definition are: `name`, `description`, `components`, `behavior`, and `state`.
```yaml
schema:
  name: model
  fields:
    - name: name
      type: string
      description: |
        The name of the model.
    - name: description
      type: string
      description: |
        An explanatory description for the model including what the
        component/system is modeling and any other relevant information.
    - name: components
      type: Field[]
      description: |
        A list of models that are components of the system.
    - name: behavior
      type: Behavior[]
      description: |
        A list of behaviors that the system being modeled will perform.
    - name: state
      type: Field[]
      description: |
        A list of data items representing internal state of the modeled
        entity. State is visible within the model but is not
        visible to other models. State may be visible between multiple
        instances of the modeled entity to support horizontal scaling.
```

# 4. Defining Enumerations
Defining enumeration values in AaC is straightforward, there is a special root key `enum` which is used to define a list of enum names. Each of the values must be unique -- enums can't have duplicate values.

As an example, the AaC DSL declares its [primitive types](https://github.com/jondavid-black/AaC/blob/bbe61782720d5958e2794308d7fe397fc6398bd3/python/src/aac/spec/spec.yaml#L240-L248) using an enum like so:
```yaml
enum:
  name: Primitives
  values:
    - string
    - int
    - number
    - bool
    - date
    - file
```

# 5. Modeling Components
So far we have covered how to define data structures and enumerations in AaC, but in order to start capturing more complex behaviors and aspects, you will need to begin modeling components. These components can be representative of whatever it is that you want -- software services, software packages, hardware components, large systems, or whatever else you're attempting to model.

Components are defined via `model` definitions; the `model` definition can capture behaviors, interfaces, and composition. You can capture overall software systems, like in the example below.
```yaml
model:
  name: AlarmClock
  description: A simple alarm clock
  behavior:
    - name: setAlarm
      type: request-response
      description: Set the alarm timer
      input:
        - name: userRequest
          type: UserRequest
      acceptance:
        - scenario: setTimer
          when:
            - The user sets the alarm timer
          then:
            - The alarm is triggered when the clock reaches the specified time
```

This also extends to modeling software systems; here is an example of a simple blogging website modelled in AaC:
```yaml
model:
  name: BlogWebsite
  description: A simple website blog
  behavior:
    - name: getBlogPost
      type: request-response
      description: Process a UserRequest and respond with a blog post
      input:
        - name: in
          type: UserRequest
      output:
        - name: out
          type: BlogPost
      acceptance:
        - scenario: getOneBlogPost
          given:
            - The API gateway is running
            - The backend service is running
            - The database is running
            - The database has at least one blog post
          when:
            - The user sends in a valid UserRequest
            - The UserRequest requests an existing blog
          then:
            - The BlogWebsite responds with content of the blog post
```

# 6. Decomposing Models
You may find that a `model` definition doesn't provide the fidelity that you need; AaC `model` definitions can be decomposed by leveraging the `components` field to define sub-components via composition.

Returning to the `AlarmClock` example, say that we want to define more than just the overall alarm clock -- we want to define and model the components of the alarm clock like the clock, timer, and alarm. We can easily do that by creating `model` definitions for each of the smaller components that we want to model including their behaviors:

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
    - name: setAlarm
      type: request-response
      description: Set the alarm timer
      input:
        - name: userRequest
          type: UserRequest
      acceptance:
        - scenario: setTimer
          when:
            - The user sets the alarm timer
          then:
            - The alarm is triggered when the clock reaches the specified time
---
model:
  name: Clock
  description: A simple clock that keeps track of the current time
    behavior:
    - name: getTime
      type: timer
      description: Get the current time
      output:
        - name: currentTime
          type: TimestampDataStructure
---
model:
  name: ClockTimer
  description: A simple timer that can be set to a target time.
  behavior:
    - name: setTime
      type: request-response
      description: Set the target time for the timer
      input:
        - name: targetTime
          type: TimestampDataStructure
    - name: triggerTimer
      type: timer
      description: Dispatch the TimerAlertDataStructure when the current time matches the target time
      input:
        - name: currentTime
          type: TimestampDataStructure
      output:
        - name: timerAlert
          type: TimerAlertDataStructure
---
model:
  name: ClockAlarm
  description: A simple alarm that produces noise.
    - name: triggerAlarm
      type: request-response
      description: Trigger the alarm noise when a TimerAlertDataStructure is received.
      input:
        - name: timerAlert
          type: TimerAlertDataStructure
      output:
        - name: alarmNoise
          type: AlarmNoise
```

# 7. Describing Model Interfaces
Model interfaces are documented via the `input` and `output` fields of their behaviors. If we refer back to our `AlarmClock` model, we can see that it has one behavior, `setAlarm`, with an input of `UserRequest`. This means that the overall alarm clock system has one input and no outputs. The input `UserRequest` is defined in our example, but we can infer that it will contain whatever data is necessary to set an alarm clock, like the target time when you want the alarm to produce noise. If we needed to add additional inputs, say we want to allow the user to set the clock time, then we would need add an additional behavior and input in our `AlarmClock` model, like so:
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
    - name: setAlarm
      type: request-response
      description: Set the alarm timer
      input:
        - name: newAlarmTimeTarget
          type: TimestampDataStructure
      acceptance:
        - scenario: setTimer
          when:
            - The user sets the alarm timer
          then:
            - The alarm is triggered when the clock reaches the specified time
    - name: setClock
      type: request-response
      description: Set the clock time
      input:
        - name: newClockTime
          type: TimestampDataStructure
      acceptance:
        - scenario: setClock
          when:
            - The user sets the alarm clock
          then:
            - The alarm clock is changed to the time provided by the user
```

# 8. Describing Model Interactions
In order to describe how your models interact with each other, you'll need to define `usecase` definitions.

Usecases have two main components:
1. The `participants` field
2. The `steps` field

The `participants` field allows you to define which models will be referenced in the usecase and to set diagram-specific names for the models such as renaming a model from "Person" to "user" in the usecase steps.

The `steps` field defines the steps, or sequence of events, that occur. Each `step` has several fields including the name, source, target, and the name of the action that occurs.

Returning to our AlarmClock example, we can see an example usecase for a user setting the alarm in our simple model.
```yaml
usecase:
  name: Set Alarm Time
  description: The user sets the time for the alarm clock.
  participants:
    - name: user
      type: Person
    - name: alarm
      type: AlarmClock
    - name: timer
      type: ClockTimer
  steps:
    - step: The user sets the time on system.
      source: user
      target: alarm
      action: setAlarm
    - step: The alarm clock stores the time in the timer
      source: alarm
      target: timer
      action: setTime
```
