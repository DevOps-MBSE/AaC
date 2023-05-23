---
layout: default
title: Creating a User Library
parent: AaC Project Structure
nav_order: 3
---
# Contributing Definitions to a User Library
One of the primary contributions a User Library type plugin would provide to AaC are definitions to be exposed to the AaC space. Definitions are a key concept and functionality within AaC, so for maximized integration and utilization for a new plugin its definitions need to be exposed to AaC. 

To do so a plugin will include its definitions as part of its registration with AaC. For registering a plugin, see [Plugins](../../old/Plugins) and [Plugin Developer Guide](../dev_guide/plugin_dev_guide)

## Inactive Plugin Definitions
When a plugin has definitions associated with it, but the plugin has not been activated, the definitions are not available for use by AaC. To confirm a plugin has been installed, but not registered, run the following command: `aac --inactive`. 
`<include a screen shot of the list results of the inactive command>`
## Active Plugin Defintions
You can activate a registered plugin by using the following command: `aac activate-plugin <plugin name>`. 
`<include screen shot of activation command>`
Verify the plugin has been activated by running the following command: `aac --active`
`<include screen shot of list results of the active command>`
Once you have verified that your plugin has been activated, you are able to check what plugin definitions, plugin commands, and such are available by running these commands: `aac <plugin name> --definitions`
`<include screen shot of list results of plugin definitions>`
`aac <plugin name> --commands`
`<include screen shot of list results of plugin commands>`

# Contributing Root Keys to a User Library

# Utilizing a User Library

## As a plugin user

## As a plugin developer