---
layout: default
title: Extending AaC Modeling Language
parent: AaC Extensions
nav_order: 1
---

# Extending the AaC Modeling Language

The AaC modeling language is self-defining...captured as an AaC model itself.  You can use the 'ext' root type
to tailor the AaC language to meet your needs.  The 'ext' root type allows you to add fields to built-in data types
or add values to built-in enumerations.

## Extensions within your model

For extensions that are specific to your model, just define an 'ext' model within your project.  That's it!

## Extensions as Plugins

If you want a cross-project extension that is more "permanent" you can create a plugin.
