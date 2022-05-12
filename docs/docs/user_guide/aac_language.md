---
layout: default
title: AaC Modeling Language Reference
parent: AaC User's Guide
nav_order: 1
---

# The AaC Modeling Language

This has not yet been written.

## Import

Describe the use of imports.

## Schema

Describe modeling data structures and self-defined language structures within a system.

## Enum

Describe modeling data with an enumerated type.

## Model

The model AaC type allows the modeler to define the logical structure
of the system and the behaviors of the elements within the logical structure.

### Components

Imagine a large system made up of many interacting components.  In an
abstract way, you can think of the design of that system as a decomposition
heirarchy starting with the system, then subsystem, then components, and modules.
The AaC model type allows this vertical decomposition to be captured using components
so that a modeler can comprehend the system at different levels of logical abstraction.

### Behavior

Behaviors are used to establish interaction points among models by specifying inputs,
outputs, and the Behavior-Driven-Development (BDD) specification for the behavior.
Using the behaviors to define interaction points enables sequences of interactions
to be modeled through use cases.

### State

The model type allows the modeler to define
internal state for the model. State represents internal data structures that persist
over time.  If modeling a horizontally scaled distributed system, state may also be
shared among instances of the modeled entity. When following design guidance such as
[12 Factor App](https://12factor.net/), maintaining state is generally to be avoided
in system module design. That said, when state is necessary it should be well defined.
The state of a model is intended to be strictly encapsulated within the model and not
visible to any other models.  Only the model's behaviors have visibility of the data
persisted as state within the model.

## Use Case

Describe the use case.

## Extension

Describe the extension.
