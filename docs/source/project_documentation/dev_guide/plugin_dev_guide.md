---
layout: default
title: Plugin Developer Guide
parent: Developer's Guide to AaC
nav_order: 5
---

# Plugin Developer Guide

## Configuration of the Environment

### AaC Setup (Prerequisites)

When performing the steps listed in the [Developer Guide](dev_guide_index), please make sure that AaC itself is executable by running the command:

`aac version`

If this command is executable please continue with this guide for developing plugins for AaC.

## Generating an AaC Project (Gen-Project Command)

AaC is a modular capability that embraces the concept of 3rd party plugins.  We recognize that your team will have unique needs and will want to tailor the AaC capability to your unique domain.  The first step in creating one or more custom plugins for your needs is to create a project.  We recommend you create a project in your Git repository manager and `clone` it to your local machine.  Create a project definition (i.e. `my_project.aac`) in the root folder.

Example project model:
```yaml
project:
  name: My project
  description: |
    An example AaC project definition.
```

You can now use the `gen-project` command to create the necessary project structure.

```bash
aac gen-project ./my_project.aac --output .
```

If you ever need a quick refresher on the gen-project command and it's options you can run:
```bash
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

This will create a project structure that looks like this:

```markdown
├── README.md
├── setup.py
├── docs
├── src
├── tests
└── tox.ini
```

## Generating AaC Plugins (Gen-Plugin Command)

AaC comes pre-packaged with a plugin called `Gen-Plugin` which will take an AaC architecture file describing a plugin and then generate the necessary code stubs project infrastructure for the user to begin implementing their new plugin.

### Gen-Plugin Usage and Output

The `gen-plugin` command can be executed as follows:

```bash
$ aac gen-plugin -h
Usage: aac gen-plugin [OPTIONS] AAC_PLUGIN_FILE

Options:
  --code-output TEXT  The location to output generated plugin code.
  --test-output TEXT  The location to output generated plugin test code.
  --doc-output TEXT   The location to output generated plugin documentation
                      code.
  --no-prompt         Informs gen-plugin to execute without asking the user to
                      confirm output paths.
  --force-overwrite   Informs generator to backup and overwrite all existing
                      files regardless of template definition.
  --evaluate          Informs generator to only write evaluation files with no
                      impact to existing files.
  -h, --help          Show this message and exit.
```

While the `gen-plugin` command will attempt to sort out directory paths for you if not provided, it's often simplest to just provide `--code-output` and `--test-output` to ensure the generated code is placed where you want it.  Currently the `gen-plugin` command doesn't output documentation, but the option is in place for future use.

#### Input of Gen-Plugin

Plugins are generated from a plugin definition.  Just as we model the AaC language with AaC, we also model plugins with AaC.  A plugin allows you to create the following:

- `commands`:  Commands are new command line interface (CLI) commands that can be executed by the user.  The `gen-project` and `gen-plugin` commands described here are examples of commands.
- `context_constraints`:  Context constraints are constraints that are executed against the the entire AaC model Language Context.  These constraints are executed after the AaC model is loaded and provide a way to check cross-cutting items within the model.
- `schema_constraints`:  Schema constraints are constraints that are executed against each schema in the AaC model.  These constraints are executed after the AaC model is loaded and context constraints are run, providing a way to check each schema in the model.
- `primitive_constraints`:  Primitive constraints are constraints that are executed against each primitive in the AaC model.  These constraints are executed after the AaC model is loaded and context constraints and schema constraints are run, providing a way to check each primitive in the model.

You have the flexibility to organize your plugins as you see fit, but it is recommended to create a `plugins` folder in your project and place your plugins in separate sub-folders to keep things organized.  This will also make the generated code more managable.  There is an expectation (or perhaps a constraint, depending on your perspective) related to file names.  Your plugin's code will be generated in a folder that aligns with the package and plugin name.  For example if your plugin has a package of "aac_example.my_plugin" and is named "My Plugin", then code will go into the `./src/aac_example/my_plugin` folder and will expect to find the plugin model named `my_plugin.aac` there. Note that the file name should be a "python-ized" version of the plugin name.  This means that spaces and dashes are replaced with underscores and the file extension is `.aac`.

Example plugin model with all possible plugin elements (not all elements are required):
```yaml
plugin:
  name: My plugin
  package: happy
  description: |
    An AaC plugin definition used to test the gen-plugin command behavior.
  commands:
    - name: test-command
      help_text: |
        A test command used to test the gen-plugin command behavior.
      run_before:
        - plugin: CheckAaC
          command: check
      run_after:
        - plugin: Generate
          command: generate
      input:
        - name: aac-plugin-file
          type: file
          description: The path to the architecture file with the plugin definition.
      acceptance:
        - name: Command test
          scenarios:
            - name: Simple Command Test
              given: 
                - An AaC file containing schemas with no extra fields.
              when:
                - The AaC check command is run on the schema.
              then:
                - The check commands provides the output 'All AaC constraint checks were successful.'
  context_constraints:
    - name: The sky is blue
      description: Ensures the sky is blue.
      acceptance:
        - name: Context test
          scenarios:
            - name: Simple Constraint Test
              given: 
                - An AaC file containing schemas with no extra fields.
              when:
                - The AaC check command is run on the schema.
              then:
                - The check commands provides the output 'All AaC constraint checks were successful.'
  schema_constraints:
    - name: Schemas have happy names
      description: Check every schema declared provides positive vibes.
      universal: true
      acceptance:
        - name: Schema test
          scenarios:
            - name: Simple Schema Test
              given: 
                - An AaC file containing schemas with no extra fields.
              when:
                - The AaC check command is run on the schema.
              then:
                - The check commands provides the output 'All AaC constraint checks were successful.'
  primitive_constraints:
    - name: Primitives have happy names
      description: Check every primitive declared provides positive vibes.
      acceptance:
        - name: Primitive test
          scenarios:
            - name: Simple Primitive Test
              given: 
                - An AaC file containing schemas with no extra fields.
              when:
                - The AaC check command is run on the schema.
              then:
                - The check commands provides the output 'All AaC constraint checks were successful.'
      
     
```

#### Output of Gen-Plugin

Let's assume we have a pluging with a package of "aac_example.plugins.plugin_name" and a name "My Plugin" with a definition that includes two acceptance tests.  This example focuses on command plugins.  More information on constraint plugins is available in the [AaC Constraint Checks](aac_constraints) documentation.  

Example plugin definition:

```yaml
plugin:
  name: My Plugin
  package: aac_example.plugins.plugin_name
  commands:
    - name: do-stuff
      inputs:
        - name: aac-file
          type: file
          description: The path to the architecture file with the plugin definition.
      acceptance:
        - name: Success test
          scenarios:
            - name: Test do stuff command with valid input
              given: 
                - A path to an existing AaC file.
              when:
                - The AaC do-stuff command is run with the path to the file
              then:
                - The do-stuff command provides the output 'SUCCESS'
        - name: Failure test
          scenarios:
            - name: Test do stuff command with valid input
              given: 
                - An path that does not point to an existing file.
              when:
                - The AaC do-stuff command is run on the file
              then:
                - The do-stuff command provides the output 'FAILURE'
```

The output of the Gen-Plugin command will be some corresponding plugin files that are templated from the AaC file that was passed in to `gen-plugin`.

The generated files are:

```markdown
└── src
|   └── aac_example
|       └── plugins
|           └── plugin_name
|               ├── __init__.py
|               └── my_plugin_impl.py
└── tests
    └── test_aac_example
        └── plugins
            └── plugin_name
                ├── __init__.py
                ├── test_my_plugin.py
                ├── my_plugin_success_test.feature
                └── my_plugin_failure_test.feature
```

The generated src folder files are:
- `__init.py__`: Auto-generated non-user-editable file that handles all the AaC plugin registration and configuration.  This file should not be edited by the user.  Rerunning gen-plugin will overwrite this file.
- `my_plugin_name_impl.py`: Autogenerated user-editable file that contains the plugin implementation.  This file is where you will implement your plugin.  Rerunning gen-plugin will not overwrite this file.

The AaC `gen-plugin` command generates all the boilerplate you need to integrate your new plugin into the AaC infrastructure.  All you need to do is implement the plugin logic in the `my_plugin_impl.py` file.  In the example above, the `my_plugin_impl.py` will contain a stub function as shown below:

```python
def do_stuff(aac_file: str) -> ExecutionResult:
    """Business logic for the do-stuff command."""
    status = ExecutionStatus.GENERAL_FAILURE
    messages: list[ExecutionMessage] = []
    error_msg = ExecutionMessage(
        "The do-stuff command is not implemented.",
        MessageLevel.ERROR,
        None,
        None,
    )
    messages.append(error_msg)

    return ExecutionResult(plugin_name, "do-stuff", status, messages)

```

To implement your desired behavior, replace the content of this generated stub.  For example, let's say all we want `do-stuff` to do is print the definition names from the AaC file to the console.  We can implement this as follows:

```python
def do_stuff(aac_file: str) -> ExecutionResult:
    """Business logic for the do-stuff command."""
    status = ExecutionStatus.SUCCESS
    messages: list[ExecutionMessage] = []
    context = LanguageContext()
    definitions = context.parse_and_load(aac_file)
    msg = ExecutionMessage(f"Definitions found in {aac_file}:  {[d.name for d in definitions]}", MessageLevel.INFO, None, None)
    messages.append(msg)

    return ExecutionResult(plugin_name, "do-stuff", status, messages)
```

The generated tests folder files are:
- `__init__.py`:  An empty init file that allows the tests to be run.  This file should not be edited by the user.  Rerunning gen-plugin will overwrite this file.
- `test_plugin_name.py`: The unit test stub for the plugin implementation.  This file is where you will implement your plugin unit tests.  Rerunning gen-plugin will not overwrite this file.
- `my_plugin_success_test.feature`: The acceptance test feature file for the plugin implementation for the success test feature.  Rerunning gen-plugin will overwrite this file.
- `my_plugin_failure_test.feature`: The acceptance test feature file for the plugin implementation for the success test feature.  Rerunning gen-plugin will overwrite this file.

AaC uses `behave` for acceptance tests.  While aac does generate the feature files, it does not generate the acceptance test steps. To automate the acceptance tests, create a subfolder called `steps` and create a file called `my_plugin_steps.py`.  If you run `behave` from the plugin folder, it will find the feature files, recognize there are no steps defined, and output stubs for the step functions.  Just cut and paste these into your `my_plugin_steps.py` file and you're ready to implement acceptance test behaviors.

Once these files have been generated, you are ready to run the `pip install` command to install the plugin.
To install the plugin make sure that you are in the directory where the `setup.py` file is located, and run `pip install -e .`
>***Note***: Be sure to use `pip`'s `-e` flag so that the plugin won't have to be reinstalled when there are changes to the plugin.

Once the plugin is installed in the python environment, when you run the `aac -h` command, the plugin that was just installed, should populate the available plugins/commands.

### Testing the Plugin

One of the files generated from the `gen-plugin` command is a test file for the plugin implementation, which is generated with a stubbed test. This templated output is only a stub, and it will need to be further developed to provide results.

After doing this the test can be executed either through VSCode or through terminal with the execution of `nose2` or `tox` commands.

### Debugging the Plugin

To debug the plugin in your VS Code editor, you will need to create a `launch.json` file in the `.vscode` folder.  The `launch.json` file should look like this:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: AAC",
            "type": "python",
            "request": "launch",
            "module": "aac",
            "args": [
                "my_plugin",
                "do-stuff",
                "my_aac_file.aac"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

You can now set breakpoints and use the VS Code testing framework to debug your plugin.
