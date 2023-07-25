---
layout: default
title: Plugin Developer Guide
parent: Developer's Guide to AaC
nav_order: 5
---

# Plugin Developer Guide

## Configuration of the Environment

### AaC Setup (Prerequisites)

When performing the steps listed in the [Developer Guide](dev_guide_index). Please make sure that AaC Plugin is executable with the execution of the below command:

`aac version`

If this command is executable please continue with this guide for developing plugins for AaC.

## Generating AaC Plugins (Gen-Plugin Command)

AaC comes pre-packaged with a plugin called `Gen-Plugin` which will take an AaC architecture file describing a plugin and then generate the necessary code stubs and python project infrastructure for the user to begin implementing their new plugin.

### Gen-Plugin Usage and Output

The `gen-plugin` command can be executed as follows: `aac gen-plugin ./path/to/architecture_file.yaml`
#### Input of Gen-Plugin

Plugins can be created with the first-party plugin `gen-plugin`. This can be executed from a shell/terminal, with the following example command:
`aac gen-plugin --help`
The above command will output the help documentation for the `gen-plugin` command with example input.

The `gen-plugin` command takes input from an architecture file and will produce a templated plugin project that can be installed as a first/third party plugin. An example plugin file is below:
> *The below example can be found under this path -> `/python/model/plugin/plugin.yaml`*

```yaml
plugin:
  name: Test Plugin
  description: |
    A test plugin with a contributed definition, a command, a definition
    validation, and a primitive validation.
  definitionSources:
    - ./definitions.yaml
  definitionValidations:
    - name: Test definition validation
  primitiveValidations:
    - name: Test primitive validation
  commands:
    - name: test-plugin-command
      helpText: Test plugin generation
      input:
        - name: architecture_file
          type: file
          python_type: str
          description: An architecture-as-code file.
      acceptance:
        - scenario: Test some stuff
          given:
            - The definitions in {{test-plugin-command.input.architecture_file}} represent a valid system architecture.
          when:
            - The command is run with the expected arguments.
          then:
            - Then stuff happens
---
schema:
  name: TestPluginData
  fields:
    - name: value1
      type: string
    - name: value2
      type: string
  validation:
    - name: Required fields are present
      arguments:
        - value1
```

#### Output of Gen-Plugin

The output of the Gen-Plugin command will be some corresponding plugin files that are templated from the `yaml` file that was passed in to `gen-plugin`

The generated files are placed into the original directory containing the AaC architecture file.

- `__init.py__`
- `plugin_name_impl.py`
- `plugin_architecture_file.yaml`
- `templates/` (The `templates/` directory will contain [Jinja](https://palletsprojects.com/p/jinja/) template files used by the plugins.)

The folder structure will look something like this for third-party plugins:

```markdown
├── README.md
├── setup.py
├── test_plugin
    ├── templates
      └── example_template.jinja2
│   ├── __init__.py
│   ├── plugin.yaml
│   └── test_plugin_impl.py
├── tests
│   └── test_test_plugin_impl.py
└── tox.ini
```

Once these files have been generated, you are ready to run the `pip install` command to install the plugin.
To install the plugin make sure that you are in the directory where the `setup.py` file is located, and run `pip install .`
>***Note***: Be sure to use `pip`'s `-e` flag so that the plugin won't have to be reinstalled when there are changes to the plugin.

Once the plugin is installed in the python environment, when you run the `aac -h` command, the plugin that was just installed, should populate the available plugins/commands.

### Registering Plugin Commands

Plugins that contribute commands to AaC must register those commands so they can be executed. To register a plugin command, we use the `register_plugin_command`decorator applied to the function that returns the `AacCommand`object defining the contributed command.

The following example shows how a plugin would register a command.

```python
@register_plugin_command(plugin_name, command_name)
def get_command_name_command():
    return AacCommand(command_name, "A command description. ", command_fn)
```

The above associates the command `command_name` with plugin `plugin_name`.

### Testing the Plugin

One of the files generated from the `gen-plugin` command is a test file for the plugin implementation, which is generated with a stubbed test. This templated output is only a stub, and it will need to be further developed to provide results.

After doing this the test can be executed either through VSCode or through terminal with the execution of `nose2` or `tox` commands.
