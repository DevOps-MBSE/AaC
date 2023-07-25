---
layout: default
title: AaC Command Line
parent: User's Guide to AaC
nav_order: 5
---

# The AaC Command Line

## Plugins and CLI Commands
The AaC package leverages a plugin architecture for modular user features; this allows users to customize the features they want from AaC. If an AaC user wants to generate code messages for the interfaces of their models they can leverage the GenProtobuf plugin, likewise they could leverage the GenDesignDoc plugin to generate markdown-based overview documents of their models. The flexibility and the target artifacts are up to the user and their needs, but all available AaC commands can be listed via the help command.

## Tab Completion

The AaC package supports tab completion for Bash, Zsh, and Fish. To set this up
for your particular shell, you must generate a completion script. After
executing the above command for your corresponding shell, source the completion
script from your shell profile script:

For Bash, run the following:

```shell
_AAC_COMPLETE=bash_source aac > ~/.aac-complete.bash
echo ". ~/.aac-complete.bash" >> ~/.bashrc
```

For Zsh, run the following:

```shell
_AAC_COMPLETE=zsh_source aac > ~/.aac-complete.zsh
echo ". ~/.aac-complete.zsh" >> ~/.zshrc
```

For Fish, run the following:

```shell
_AAC_COMPLETE=fish_source aac > ~/.config/fish/completions/aac-complete.fish
```

## The Help Command
AaC has a help command for the CLI that can be invoked via `aac -h`. Successfully invoking the help command is an easy way to check if your installation of AaC is working. For each installed and active plugin, they will contribute to the comands visible in the help output text, similar to:
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

 Each plugin command that is listed can be further interrogated by using the help flag after the command name `aac <command> -h`, which will return all of the arguments for that particular command.

For example, if I wanted to see what the options and arguments for the `puml-sequence` command it would look something like:
```
$ aac puml-sequence -h
usage: aac puml-sequence [-h] architecture_file output_directory

positional arguments:
  architecture_file  Path to a yaml file containing an AaC usecase from which to generate a Plant UML sequence diagram.
  output_directory   Output directory for the PlantUML (.puml) diagram file

optional arguments:
  -h, --help         show this help message and exit
```

*If you expect to see a command that's not present, it's likely that the plugin providing the command has not been installed correctly.*

## Built-In Commands
While AaC primarily sources CLI commands from plugins, AaC has a couple foundational commands that will always be present regardless of which plugins you have enabled or installed.

### Version
The version command provides an easy-to-access semantic version of the AaC python tool.

Usage:
```
$ aac version
version: success

0.2.1
```

### Validate
The validate command provides the ability to validate an AaC file or a definition therein.

To validate an AaC file, and any files it may import, run the validate command with a single argument which is the path to the file you want to validate.
```
$ aac validate model/alarm_clock/alarm_clock.yaml
validate: success

model/alarm_clock/alarm_clock.yaml is valid.
```

Alternatively, if you only wanted to validate a single definition in a file, you can use a optional argument `--definition_name insert_name_here` to signal to the validation plugin that it should only validate the definition with the corresponding name in the file.
```
$ aac validate model/alarm_clock/alarm_clock.yaml --definition_name AlarmClock
validate: success

'AlarmClock' in model/alarm_clock/alarm_clock.yaml is valid.
```

If you attempt to selectively validate a single definition, but fail to choose the name of a definition in the file, the plugin will return some suggestions such as names of definitions in your target file or the actual file containing the definition you selected:
```
$ aac validate model/alarm_clock/alarm_clock.yaml --definition_name Primitives
validate: plugin_failure

'Primitives' was not found in the file.
Definitions available in 'model/alarm_clock/alarm_clock.yaml' are ['AlarmClock', 'Clock', 'ClockTimer', 'ClockAlarm', 'TimerAlert', 'Timestamp', 'TimezoneOffset', 'AlarmNoise']
Definition 'Primitives' can be found in '/workspace/AaC/python/src/aac/spec/spec.yaml'
```
