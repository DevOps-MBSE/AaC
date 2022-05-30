---
layout: default
title: AaC Command Line
parent: AaC User's Guide
nav_order: 3
---

# The AaC Command Line

The AaC package leverages a plugin architecture for modular user-features; this allows users to customize the features they want from AaC. If an AaC user wants to generate code messages for the interfaces of their models they can leverage the GenProtobuf plugin, likewise they could leverage the GenDesignDoc plugin to generate markdown-based overview documents of their models. The flexibility and the target artifacts are up to the user and their needs, but all available AaC commands can be listed via the help command.

Executing the help command via the CLI via `aac -h` will return the list of available plugin commands based on the currently installed plugin. Each plugin command that's listed can be further interrogated by using the help flag after the command name `aac <command> -h`, which will return all of the arguments for that particular command.

For example, if I wanted to see what the options and arguments for the `puml-sequence` it would look something like:
```
$ aac puml-sequence -h
usage: aac puml-sequence [-h] [--output_directory OUTPUT_DIRECTORY] architecture_file

positional arguments:
  architecture_file     Path to a yaml file containing an AaC usecase from which to generate a Plant UML sequence diagram.

optional arguments:
  -h, --help            show this help message and exit
  --output_directory OUTPUT_DIRECTORY
                        Output directory for the PlantUML (.puml) diagram file
```

*If you expect to see a command that's not present, it's likely that the plugin providing the command has not been installed correctly.*