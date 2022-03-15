---
layout: default
title: AaC Plugins
nav_order: 3
has_children: true
permalink: docs/plugins
---

# AaC Plugins

## Built-In Plugins for Core Commands

AaC leverages a plugin architecture to implement the majority of its user features providing an extensible interface for the core development team and any other party interested in contributing to AaC. Built-in plugins that provide features like `Gen-Plugin` and `Gen-JSON` are maintained inside the repository and are shipped alongside the core AaC package. This support and maintenance by the core development team is why we classify these built-in plugins as "first-party".

### JSON

AaC includes a built-in command to convert your AaC YAML model to JSON.
```bash
aac json <aac_model.yaml>
```

### Plugin Generator

AaC includes a built-in command to help you extend AaC by creating your own plugins. This is how we build all of our plugins.
```bash
aac gen-plugin <path/to/aac_plugin_model.yaml>
```

The plugin generator does support generating first-party and third-party plugins. The generator uses the path of AaC plugin file to identify if it is within an AaC repository, if the path contains "src/aac/plugins/" then the plugin is classified as being a first-party plugin. Otherwise, if the path doesn't contain "src/aac/plugins/" then the plugin is assumed to be third-party and is generated with an independent python project skeleton.

## Third Party Plugins

AaC can be extended by anyone, wether they are part of our core team or not.  We recommend any plugin developer
use the "aac-" prefix when building and puglishing AaC plugins.  Search (PyPI)[https://pypi.org/] for additional 3rd party Plugins.

## AaC Core Plugins

AaC core plugins are built and published by our team but are not part of the AaC distribution.  We want AaC to be
as useful as possible, but not bloated.  As we extend the functionality of AaC, expect to see more core plugins published.
