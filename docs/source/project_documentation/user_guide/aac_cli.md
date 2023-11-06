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
Usage: aac [OPTIONS] COMMAND [ARGS]...

  The Architecture-as-Code (AaC) command line tool.

Options:
  -h, --help  Show this message and exit.

Commands:
  check        Perform AaC file quality checks using defined constraints in
               the AaC models.
  clean        Remove backup and evaluation files from prior aac file
               generation.
  gen-plugin   Generate code and stubs for an AaC plugin.  Overwrites will
               backup existing files.
  gen-project  Generate code and stubs for an AaC project.  Overwrites will
               backup existing files.
  generate     Performs content generation based on user defined templates.
  print-defs   Print YaML representation of AaC language definitions.
  version      Print the AaC package version.
```

 Each plugin command that is listed can be further interrogated by using the help flag after the command name `aac <command> -h`, which will return all of the arguments for that particular command.

For example, if I wanted to see what the options and arguments for the `gen-project` command it would look something like:
```shell
$ aac gen-project -h
Usage: aac gen-project [OPTIONS] AAC_PROJECT_FILE

Options:
  --output TEXT      The location to output generated plugin code.
  --no-prompt        Informs gen-plugin to execute without asking the user to
                     confirm output paths.
  --force-overwrite  Informs generator to backup and overwrite all existing
                     files regardless of template definition.
  --evaluate         Informs generator to only write evaluation files with no
                     impact to existing files.
  -h, --help         Show this message and exit.
```

## Built-In Commands
AaC sources CLI commands from plugins.  AaC provides a foundational set of commands that will always be present.

- [check](../plugins/check):  Ensures your model is correctly defined per the AaC DSL
- [version](../plugins/version): Get the version of the AaC package installed
- [generate](../plugins/generate):  General purpose plugin for generating files from your model
- [gen-plugin](../plugins/gen_plugin): Generate a new AaC plugin
- [print-defs](../plugins/print_defs): Print the definitions of your model as YAML (useful for reference)
