---
layout: default
title: AaC Command Line
parent: AaC User's Guide
nav_order: 3
---

# The AaC Command Line

The AaC package leverages a plugin architecture for modular user features; this allows users to customize the features they want from AaC. If an AaC user wants to generate code messages for the interfaces of their models they can leverage the GenProtobuf plugin, likewise they could leverage the GenDesignDoc plugin to generate markdown-based overview documents of their models. The flexibility and the target artifacts are up to the user and their needs, but all available AaC commands can be listed via the help command.

If AaC is properly installed, the `aac -h` command output will look similar to:
```
usage: aac [-h]
           {help-dump,start-lsp-io,start-lsp-tcp,print-spec,print-active-context,spec-validate,puml-component,puml-sequence,puml-object,gen-gherkin-behaviors,gen-design-doc,gen-protobuf,gen-plugin,gen-json,version,validate}
           ...

positional arguments:
  {help-dump,start-lsp-io,start-lsp-tcp,print-spec,print-active-context,spec-validate,puml-component,puml-sequence,puml-object,gen-gherkin-behaviors,gen-design-doc,gen-protobuf,gen-plugin,gen-json,version,validate}
    help-dump                 Produce a formatted string containing all commands, their arguments, and each of their descriptions.
    start-lsp-io              Start the AaC Language Server Protocol (LSP) server in IO mode
    start-lsp-tcp             Start the AaC Language Server Protocol (LSP) server in TCP mode
    print-spec                Print the AaC model describing core AaC data types and enumerations.
    print-active-context      Print the AaC active language context including data types and enumerations added by plugins.
    ...
    version                   Print the AaC package version.
    validate                  Validate the AaC definition file.

optional arguments:
  -h, --help                  show this help message and exit
```

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