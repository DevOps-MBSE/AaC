---
layout: default
title: Plugin Developer Guide Documentation
parent: Developer's Guide to AaC
nav_order: 5
---

# Plugin Developer Guide Documentation

## Contributing to the AaC Project

### How to Contribute to the Project

To contribute to the project, the following will need to be provided to the Project Owner for AaC:
>***Note***: The AaC Project is currently being limited to outside contributions, If interested in contributing to this project please contact the Project Owner for AaC, 
> to be added at a later time.

- Name
- Descriptions of what will be contributed
- Purpose and context of the contribution and its impact on the project if implemented. 

This list may expand to include other additional information needed as the project expands and developments are made.

## Configuration of the Environment

### AaC Setup (Prerequisites)

When performing the steps listed in the [Developer Guide](./index.md). Please make sure that AaC Plugin is executable with the execution of the below command:

`aac version`

If this comamnd is executable please continue with this guide for developing plugins for AaC. 

## AaC Generating Plugins (Gen-Plugin Comamnd)

### How to Use Gen-Plugin and Output

#### Input of Gen-Plugin

Plugins can be created with the first-party plugin `gen-plugin`. This can be executed from a shell/terminal, with the following example command:
`aac gen-plugin -help`
The above comamnd will output the help documentation for the `gen-plugin` comamnd with example input.

The `gen-plugin` command takes input from an architecture file and will produce an output of templated plugin files that can be used to install the first/third party plugin that is being developed. An example plugin file is below:
> *The below example can be found under this path -> `/python/model/plugin/plugin.yaml`*

```yaml
model:
  name: test-plugin
  description: first-party is a test plugin
  behavior:
    - name: test-plugin-command
      type: command
      description: Test plugin generation
      input:
        - name: architecture_file
          type: file
          python_type: str
          description: An architecture-as-code file.
      acceptance:
        - scenario: Test some stuff
          given:
            - The {{test-plugin-command.input.architecture_file}} represent a valid system architecture.
          when:
            - The command is run
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

The output of the Gen-Plugin comamnd will be some corresponding plugin files that are templated from the `yaml` file that was passed in to `gen-plugin`

The files that are generated are the following files in a new folder in the directory where the command was executed (Location of the `yaml` file).

- `__init.py__`
- `plugin_name_impl.py`
- `plugin_architecture_file.yaml`
- `jinja` template files will also be generated for the generated plugin

The folder structure will look something like this:

```markdown
├── README.md
├── setup.py
├── test_plugin
    ├── templates
    	└── jinja_templates
│   ├── __init__.py
│   ├── plugin.yaml
│   └── test_plugin_impl.py
├── tests
│   └── test_test_plugin_impl.py
└── tox.ini
```

Once these files have been generated, you are ready to run the `pip install` command to install the plugin.
To install the plugin make sure that you are in the directory where the `setup.py` file is located, and run `pip install .`

Once the plugin is installed in the python environment, when you run the `aac -h` command, the plugin that was just installed, should populate the available plugins/comamnds.

### Testing the Plugin

One of the files generated from the `gen-plugin` comamnd is that a test file for the plugin implementation will be generated. This templated output of a test will need to be further written though to produce quantifiable results. 

After doing this the test can be executed either through VSCode or through terminal with the execution of `nose2` or `tox` commands. 

###
