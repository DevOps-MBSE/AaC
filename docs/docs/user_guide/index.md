---
layout: default
title: AaC User's Guide
nav_order: 2
has_children: true
permalink: docs/userguide
---

# Getting started

## Installing AaC

AaC is written in python to help make it more approachable for casual users and easily extensible for
power users.  You will need Python 3.9 or later to run AaC.

To install AaC on Linux or Windows:
```bash
pip install aac
```

Usage information is available from the command line interface:
```bash
aac --help
```
The core functionallity of AaC provides commands to:
- validate:  Ensures your model is correctly defined.
- json:  Convert your model from yaml to json.
- gen-plugin:  Generate a new AaC plugin using behavior in an AaC model.

## Installing Plugins
Plugins are available to extend the functionallity of AaC.

To install an AaC Plugin on Linux or Windows:
```bash
pip install <aac-plugin>
```

If the plugin provides new command functionallity you can see the details in the usage information.
```bash
aac --help
```

# Using AaC to Model Your System

To use AaC you first define a model of your system in yaml.  Refer to the documentation for more details.
A simple model for an EchoService is provided here for reference.  Cut and paste the below model into a 
file called EchoService.yaml.  
*Note: This is using a little yaml trick to concatenate the content of two yaml files into a single file.*
```yaml
data: 
  name: Message
  fields:
  - name: body
    type: string
  - name: sender
    type: string
---
model:
  name: EchoService
  description: This is a message mirror.
  behavior:
    - name: echo
      type: request-response
      description: This is the one thing it does.
      input:
        - name: inbound
          type: Message
      output:
        - name: outbound
          type: Message
      acceptance:
        - scenario: onReceive
          given:
           - The EchoService is running.
          when:
            - The user sends a message to EchoService.
          then:
            - The user receives the same message from EchoService.
```

Now you can run AaC against your model.
```bash
aac validate EchoService.yaml
```

AaC has some core "root types" for you to work with.  You can see the root types of **data** and **model** used in the example above.
The AaC core root types are:
- data: Allows you to model data types used within your system as named types with fields.
- enum: Allows you to model enumerated types (types with only specific values allowed).
- model: Allows you to model the behavioral elements of your system.  These can be abstract or concrete.
- usecase: Allows you to model the sequence of interactions between your models.
- ext: Allows you to easily extend the AaC model itself and tailor things to your needs.

Although you can use the yaml trick above when modelling your system, it would be better to keep things more 
structured and organized.  To help with this AaC allows you to define each item you model in a separate file and
then import it as needed.  To do this just put an **import** at the root of your model file.  

Here's an example of the EchoService broken into two files:
- Message.yaml

    ```yaml
    data: 
    name: Message
    fields:
    - name: body
        type: string
    - name: sender
        type: string
    ```
- EchoService.yaml

    ```yaml
    import:
    - ./Message.yaml
    model:
    name: EchoService
    description: This is a message mirror.
    behavior:
        - name: echo
        type: request-response
        description: This is the one thing it does.
        input:
            - name: inbound
            type: Message
        output:
            - name: outbound
            type: Message
        acceptance:
            - scenario: onReceive
            given:
            - The EchoService is running.
            when:
                - The user sends a message to EchoService.
            then:
                - The user receives the same message from EchoService.

    ```
Ok, so that's interesting, but what can you do with the AaC model once you've built it?
AaC is designed and built on years of experimentation, experience, and learning.  That said, this version
is a brand new implementation rewritten entirely in Python in an attempt to make AaC more user friendly
to both the casual user and the power user. Right now AaC doesn't have a lot of additional features.
New plugins are being created to deliver more functionallity.  Over time there will be plugins
available to use the AaC model to auto-generate content for reviews, documentation, and even system
devleopment and deployment.  Check back for frequent updates and releases.
