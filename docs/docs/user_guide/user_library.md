---
layout: default
title: Creating a User Library
parent: User's Guide to AaC
nav_order: 3
---
# Contributing Definitions to a User Library
One of the primary contributions a User Library type plugin would provide to AaC are definitions to be exposed to the AaC space. Definitions are a key concept and functionality within AaC, so for maximized integration and utilization for a new plugin its definitions need to be exposed to AaC. To understand more about definitions and their role in AaC, see [Definitions](./aac_language/#definitions) section of the AaC Modeling Language Reference page.

To do so a plugin will include its definitions as part of its registration with AaC. For registering a plugin, see [Plugins](../../old/Plugins) and [Plugin Developer Guide](../dev_guide/plugin_dev_guide)

## Inactive Plugin Definitions
When a plugin has definitions associated with it, but the plugin has not been activated, the definitions are not available for use by AaC. To confirm a plugin has been installed, but not registered, run the following command: `aac --inactive`.

`<include a screen shot of the list results of the inactive command>`
## Active Plugin Defintions
You can activate a registered plugin by using the following command: `aac activate-plugin <plugin name>`.

`<include screen shot of activation command>`

Verify the plugin has been activated by running the following command: `aac --active`

`<include screen shot of list results of the active command>`

Once you have verified that your plugin has been activated, you are able to check what plugin definitions, plugin commands, and such are available by running these commands: `aac <plugin name> --definitions` *think this is the correct command, please correct if not*

`<include screen shot of list results of plugin definitions>`

`aac <plugin name> --commands` *think this is the correct command, please correct if not*

`<include screen shot of list results of plugin commands>`

# Contributing Root Keys to a User Library
A Root Key is another key concept of AaC that provides functionality and extensibility to a plugin because of AaC's usage of YAML. For information on pre-defined Root Keys, see the [Root Keys](./aac_language/#root-keys) section of the AaC Modeling Language Reference page.

## Defining, adding, and leveraging a Root Key
A Root Key is a way of creating a representation for a type of element to be leveraged by AaC. So if a plugin is planning to provide a different type of element than what is in the base DSL, the new Root Keys need to be defined in a similar manner as wthin the [core spec](https://github.com/jondavid-black/AaC/blob/bbe61782720d5958e2794308d7fe397fc6398bd3/python/src/aac/spec/spec.yaml#L2-L6).

There is information about how the core spec is utilized as well as information and an example of how to extend the DSL for use via an additional plugin within the [Base DSL and Extended DSL](./aac_language/#the-base-dsl-core-spec) sections of the AaC Modeling Language Reference page.

# Utilizing a User Library
*Not sure what additional information would really need to go in these pieces that isn't covered by the other plugin documentation pages*
## As a plugin user
For information about creating or using a User Library Plugin as a user, see [User's Guide to AaC](./index)

## As a plugin developer
For information about creating or using a User Library Plugin as a developer, see [Developer's Guide to AaC](../dev_guide/index).
