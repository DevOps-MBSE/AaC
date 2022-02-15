---
layout: default
title: AaC Developer's Guide
nav_order: 2
has_children: true
permalink: docs/dev_guide
---

# Getting started

## Gitpod Environment
This project prioritizes supporting accessible, reproduceable, and easy to use development environments which is why we support and recommend users use the already-curated [Gitpod](https://www.gitpod.io/) Architecture-as-Code development environment. In fact, you can open a Gitpod instance right now by clicking this link: https://Gitpod.io/#https://github.com/jondavid-black/AaC. The Gitpod environment handles all the setup and configuration necessary to begin developing AaC. You can immediately open a vscode workspace file and begin debugging the Python and Typescript applications.

If it's your first time using Gitpod, you'll be prompted to make an account or use SSO provided by gitlab and github. Gitpod provides a free tier, so you're not required to pay before using it.

Gitpod provides the ability to initialize the environment with shell commands and scripts. We leverage these init commands to prime a development environment (terminal) for the AaC Python package and the AaC VSCode Extension (Typescript). You can find the init commands in the `.Gitpod.yml` file at the root of the repository.

## Non-Gitpod Environment

### Requirements
There are some development requirements for developing with AaC. The always up-to-date source of truth for requirements will be the `.gitpod.Dockerfile` at the root of the AaC repository.
* Python 3.9+ Installed
* Typescript Dependencies
    * libnss3-dev
    * libgbm-dev

### Installing AaC Python Package
We expect python developers to use a virtual environment when developing the AaC package, and so the project is configured only for use with virtual environments.

Create a new environment:
```bash
python3.9 -m venv venv --system-site-packages
```

Configure your shell with the virtual environment:
```bash
source venv/bin/activate
```

Install the AaC package in development mode:
```bash
pip install -e .[all]
```

Run the AaC `version` command to confirm the package is installed:
```bash
aac version
```

<br>

#### AaC Python Package Dependency Control
For more fine-grained control when installing dependencies, they have been structured into 3 sections:
- runtime - the dependencies required to run the project
- test - the dependencies required to run the project's automated tests
- dev - the dependencies required to run development tools like linting and quality checks

To install only runtime dependencies simply use pip to install the dependencies:
```bash
$ pip install -e .
```

If you'd like to install the additional dependencies (test and dev), then you can specify that pip include those dependencies like such:

To install test dependencies (test), run this:
```bash
$ pip install -e .[test]
```

To install development dependencies (dev), run this:
```bash
$ pip install -e .[dev]
```

To install all dependencies (runtime, dev, and test), run this:
```bash
$ pip install -e .[all]
```

### Running the AaC VSCode Extension
The Typescript VSCode Extension can be run by

## VSCode Workspaces
Because this repository houses both a Python and TypeScript project, we're using [VSCode Workspaces](https://code.visualstudio.com/docs/editor/workspaces) to separate and present two different projects and experiences. When you first open the project in VSCode, you will see the entirety of it, however, if you open say the python workspace then the VSCode instance will reload and now the visible files, IDE configuration, and the configured tasks are all pertaining to the python package. The same is true for the vscode_extension workspace and its configuration for TypeScript.

You can open a workspace in VSCode by:
1. Hitting the `f1` key
2. When prompted, type `Open Workspace From File`
3. When presented with a filepath, enter:
    - /workspace/AaC/.vscode/python.code-workspace
    - /workspace/AaC/.vscode/vscode_extension.code-workspace
4. Press the `Ok` button and watch the IDE switch workspaces.