# Architecture-as-Code VSCode Extension

VSCode Extension that wraps the Python3 package
[`aac`](https://pypi.org/project/aac/). This extension provides AaC commands at
your fingertips within VSCode as well as providing language server features for
an easier, more productive experience with AaC.

The AaC VSCode extension does not require configuration as long as the `aac`
Python tool is in your `PATH`. Nonetheless, there are configuration options
available, so for detailed instructions on configuring the AaC VSCode Extension,
refer to [this](https://jondavid-black.github.io/AaC/docs/vscode_extension) page.

## Features

Provides the complete list of AaC commands as VSCode Tasks. See
[here](https://jondavid-black.github.io/AaC/docs/vscode_extension/command_features) for
more information.

Provides an AaC Language Server. See
[here](https://jondavid-black.github.io/AaC/docs/vscode_extension/lsp_features) for more
information.

### Architecture-as-Code Language Server Protocol (LSP)
The AaC VSCode extension integrates with the AaC python package to provide IDE language features for AaC files.

### Visual Definition Editor
The AaC VSCode extension can leverage the AaC python package's `rest-api` plugin to provide VSCode users with an in-IDE visual editor for AaC definitions.

Before getting started, make sure that you have the AaC `rest-api` plugin running in your project directory.
```bash
aac rest-api --host <hostname|localhost> --port <8000>
```

## Requirements

This plugin relies on the Python package [`aac`](https://pypi.org/project/aac/).
In order to use this plugin, you must install `aac` locally. See the [AaC
Repository](https://github.com/jondavid-black/AaC#using-aac-to-model-your-system)
for how to install the AaC package.

Once the `aac` package is installed, verify that the installation is working
correctly by running `aac -h` in a terminal. If you are presented with a list of
commands with accompanying descriptions, the installation was successful.

## Known Issues

The Visual Editor is in an early prototype mode, and so there are some issues such as a lack of feedback when a user saves a definition via the visual editor.

YAML files do not automatically get imported, unlike AaC files.

## Release Notes

### 0.0.3 Early Prototype
* Included an early version of the Visual Editor
* Added LSP support for AaC files
* Provided an initial walkthrough for users