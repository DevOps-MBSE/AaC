# Getting Started as a Developer

## VSCode

You can open the AaC folder in your VSCode editor and start working across the entire repository.  Historically this repository has housed various sub projects, but have since refactored into a multi-repo structure with only the main AaC capability in the main repository.  As such we'd previously setup [VSCode Workspaces](https://code.visualstudio.com/docs/editor/workspaces) to separate projects and experiences.  We opted to keep the Python project in place during the refactor. 

When you first open the project in VSCode, you will see the entirety of it, however, if you open the Python workspace then the VSCode instance will reload and now the visible files, IDE configuration, and the configured tasks will now pertain only to the Python package. We'll maintain this flexibility for now in case we discover a need for another project within the repository.

You can open a workspace in VSCode by:

1. Hitting the `f1` key
2. When prompted, type `Open Workspace From File`
3. When presented with a filepath, enter:
    - /path/to/workspace/AaC/.vscode/python.code-workspace
4. Press the `Ok` button and watch the IDE switch workspaces.

---

## Gitpod Environment

This project prioritizes accessible, reproducible, and easy to use development environments which is why we support and recommend users take advantage of the already-curated [Gitpod](https://gitpod.io/new/#https://github.com/DevOps-MBSE/AaC) Architecture-as-Code development environment. The Gitpod environment handles all the setup and configuration necessary to begin developing AaC. You can immediately open the project in VSCode and begin modifying and debugging the Python application.

If it's your first time using Gitpod, you'll be prompted to make an account or use SSO provided by GitLab and GitHub. Gitpod provides a free tier, so you're not required to pay before using it.

Gitpod provides the ability to initialize the environment with shell commands and scripts. We leverage these init commands to handle any initialization for the AaC Python package, such as installing dependencies and building the project. You can find the init commands in the `.gitpod.yml` file at the root of the repository.

## Non-Gitpod Environment

### Requirements

There are some developmental and system requirements for developing with AaC.

1. Python 3.9+ Installed

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
# from the current working directory:
flake8 .

# or give a path to the file you want to lint
flake8 ./path/to/file.py
```

Additionally, to get an HTML code coverage report, update the `tox` command to include the following flags: `tox -- --coverage-report html`

#### VSCode Unit Test Support for Python

The Python plugin for VSCode supports the `unittest` Python library, and not the `nose2` framework that we use. The impact is fairly minimal, but Python unit tests using the `nose2` parameterized test feature will not run correctly from within the VSCode IDE since it fails to recognize the `nose2` parameterized tests as parameterized tests, which causes them to fail.

To get around this, you can run all the tests from the terminal using the above `tox` commands.

## AaC Profiling Developer Guide

### Profiling in AaC

The type of profiling that is being described for the AaC Python Package is between using the `cProfile` (C-backed) or `Profile` (Python-backed). These two profilers are considered to be *deterministic* profilers. A *profile*
is a set of statistics that help to determine which portions of code are being run often and for how long. This can help to identify the flow of execution. Using the output data from these profilers can be imported into `pstats`
for reporting.

Documentation on the Setup and Justifications between the `cProfile` and `Profile` can be located here -> [Profiling in AaC Setup](profiling)

## Development of Plugins

Guidelines on how to contribute and develop plugins for AaC can be found in [Plugin Developer Guide](plugin_dev_guide).
