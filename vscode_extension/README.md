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

## Extension Settings


### pythonPath
The filesystem path to the Python3 executable. If using a virtual environment, use the path to the virtual environment Python executable.

The default value is `/usr/local/bin`.

### aacPath
The filesystem path to the aac CLI tool. MUST be set in order to for the AaC VSCode extension to start up the LSP server in IO mode.

### lsp.serverMode
The mode of communication with the LSP server. IO is default, but TCP will allow for connection to already established LSP servers.

### lsp.tcp.host
The hostname of of the LSP server. Used to establish a TCP connection.

### lsp.tcp.port
The port of of the LSP server. Used to establish a TCP connection.

### rest_api.host
The host to use for establishing a TCP connection with the AaC REST API plugin.

### rest_api.port
The port to use for establishing a TCP connection with the AaC REST API plugin.

## Known Issues

None yet.

## Release Notes

### 0.0.1 Initial Pre-release
*