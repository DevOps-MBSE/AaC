---
layout: default
title: AaC Plugins
nav_order: 3
has_children: true
permalink: docs/plugins
---

# AaC Plugins

## Built-In Plugins for Core Commands

AaC is published with a small set of built-in plugins.

### JSON

AaC includes a built-in command to convert your AaC YAML model to JSON.
```bash
aac json <aac_model.yaml>
```

### Plugin Generator

AaC includes a built-in command to help you extend AaC by creating your own plugins.  This is how we build core plugins.
```bash
aac gen-plugin <aac_model.yaml>
```
## 3rd Party Plugins

AaC can be extended by anyone, wether they are part of our core team or not.  We recommend any plugin developer
use the "aac-" prefix when building and puglishing AaC plugins.  Search (PyPI)[https://pypi.org/] for additional 3rd party Plugins.

## AaC Core Plugins

AaC core plugins are built and published by our team but are not part of the AaC distribution.  We want AaC to be 
as useful as possible, but not bloated.  As we extend the functionallity of AaC, expect to see more core plugins published.
