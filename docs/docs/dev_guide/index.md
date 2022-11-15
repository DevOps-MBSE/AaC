---
layout: default
title: Developer's Guide to AaC
nav_order: 6
has_children: true
---

# Getting started

## VSCode Workspaces

Because this repository houses both a Python and TypeScript project, we're using [VSCode Workspaces](https://code.visualstudio.com/docs/editor/workspaces) to separate and present two different projects and experiences. When you first open the project in VSCode, you will see the entirety of it, however, if you open say the Python workspace then the VSCode instance will reload and now the visible files, IDE configuration, and the configured tasks will now pertain only to the Python package. The same is true for the vscode_extension workspace and its TypeScript configuration.

You can open a workspace in VSCode by:

1. Hitting the `f1` key
2. When prompted, type `Open Workspace From File`
3. When presented with a filepath, enter:
    - /path/to/workspace/AaC/.vscode/python.code-workspace
    - /path/to/workspace/AaC/.vscode/vscode_extension.code-workspace
4. Press the `Ok` button and watch the IDE switch workspaces.

---

## Gitpod Environment

This project prioritizes supporting accessible, reproducible, and easy to use development environments which is why we support and recommend users use the already-curated [Gitpod](https://www.gitpod.io/) Architecture-as-Code development environment. In fact, you can open a Gitpod instance right now by clicking this link: https://Gitpod.io/#https://github.com/jondavid-black/AaC. The Gitpod environment handles all the setup and configuration necessary to begin developing AaC. You can immediately open a vscode workspace file and begin debugging the Python and Typescript applications.

If it's your first time using Gitpod, you'll be prompted to make an account or use SSO provided by Gitlab and Github. Gitpod provides a free tier, so you're not required to pay before using it.

Gitpod provides the ability to initialize the environment with shell commands and scripts. We leverage these init commands to handle any initialization for the AaC Python package and the AaC VSCode Extension (Typescript), such as installing dependencies and building the projects. You can find the init commands in the `.Gitpod.yml` file at the root of the repository.

## Non-Gitpod Environment

### Requirements

There are some developmental and system requirements for developing with AaC.

1. Python 3.9+ Installed
2. Typescript Development Dependencies

#### Linux Requirements

Developing the VSCode extension in linux environments may require the installing of additional OS dependencies.

- *libnss3-dev*
- *libgbm-dev*

### Developing the AaC Python Package

The AaC Python package, its source code, and its configuration are all found in the `python/` directory.

#### Installing AaC Python Package

We expect Python developers to use a virtual environment when developing the AaC package, and so the project is configured only for use with virtual environments.

Create a new environment:

`bash` and `zsh` command:

```bash
python3.9 -m venv venv --upgrade-deps
```

Or if you're developing in a containerized environment:

`bash` and `zsh` command:

```bash
python3.9 -m venv venv --upgrade-deps --system-site-packages
```

Configure your shell with the virtual environment:

`bash` and `zsh` command:

```bash
source venv/bin/activate
```

Install the AaC package in development mode:

`bash` command:

```bash
pip install -e .[all]
```

`zsh` command:

```zsh 
pip install -e '.[all]'
```

Run the AaC `version` command to confirm the package is installed:

`bash` and `zsh` command:

```bash
aac version
```

#### AaC Python Package Dependency Control

For more fine-grained control, we have three separate categories of dependencies that can be installed:

- runtime - the dependencies required to run the project
- test - the dependencies required to run the project's automated tests
- dev - the dependencies required to run development tools like linting and quality checks

To install only runtime dependencies simply use pip to install the dependencies:

```bash
pip install -e .
```

If you'd like to install the additional dependencies (test and dev), then you can specify that pip include those dependencies like such:

To install test dependencies (test), run this:

`bash` command:

```bash
pip install -e .[test]
```

`zsh` command:

```zsh
pip install -e '.[test]'
```

To install development dependencies (dev), run this:

`bash` command:

```bash
pip install -e .[dev]
```

`zsh`command:

```zsh
pip install -e '.[dev]'
```

To install all dependencies (runtime, dev, and test), run this:
`bash` command:

```bash
pip install -e .[all]
```

`zsh` command:

```zsh
pip install -e '.[all]'
```

#### Testing the Python Package

To run tests, make sure you've set up your dependencies using `pip install -e .[test]` or `pip install -e .[all]` (or the `ZSH` equivalents). Then, from the root of the Python project, run the following shell command (from within your virtual environment).
`bash` and `zsh` command:

```bash
tox
```

Alternatively, for use with a linter such as `flake8` you could run the following shell command from the root of your working directory:

```bash
// from the current working directory:
flake8 .

// or give a path to the file you want to lint
flake8 ./path/to/file.py
```

Additionally, to get an HTML code coverage report, update the `tox` command to include the following flags: `tox -- --coverage-report html`

#### VSCode Unit Test Support for Python

The Python plugin for VSCode supports the `unittest` Python library, and not the `nose2` framework that we use. The impact is fairly minimal, but Python unit tests using the `nose2` parameterized test feature will not run correctly from within the VSCode IDE since it fails to recognize the `nose2` parameterized tests as parameterized tests causing them to fail.

To get around this, you can run all the tests from the terminal using the above `tox` commands.

### Developing the AaC TypeScript VSCode Extension

The TypeScript AaC VSCode Extension, its source code, and its configuration are all found in the `vscode_extension/` directory.

#### Installing & Building the AaC VSCode Extension

The TypeScript VSCode Extension can be installed by running:
`bash` and `zsh` command:

```bash
yarn compile
```

#### Running the AaC VSCode Extension

Assuming that the Typescript VSCode Extension workspace is currently open and active, the VSCode extension can be debugged in VSCode by opening an extension typescript file, hitting the `f5` key, and selecting "VSCode Extension Development" from the debug run configurations.

Assuming all went well, VSCode will launch another instance of the IDE with the AaC Extension installed.

## AaC Profiling Developer Guide

### Profiling in AaC
The type of profiling that is being described for the AaC Python Package is between using the `cProfile` (C-backed) or `Profile` (Python-backed). These two profilers are considered to be *deterministic* profilers. A *profile*
is a set of statistics that help to determine which portions of code are being run often and for how long. This can help to identify areas of *recursion*. Using the output data from these profilers can be imported into `pstats`
for use of reporting.

Documentation on the Setup and Justifications between the `cProfile` and `Profile` can be located here -> [Profiling in AaC Setup](./profiles/profiling.md
