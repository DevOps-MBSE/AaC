# Generate Plugin

The `gen-plugin` plugin generates the boilerplate integration code for your modeled AaC plugin.  This supports generation of a new AaC project or plugin(s) within an existing project.  This will ensure that your plugin is properly integrated with the AaC framework and can be used by the AaC CLI.  Generated plugins provide the code infrastructure for you to define new AaC commands and constraints by completing stubbed out functions.

## Gen-Plugin Command

![Gen-Plugin Terminal Output](../../images/examples/gen-plugin-terminal-output.png)

![Gen-Plugin File Output](../../images/examples/gen-plugin-file-output.png)

## Arguments

### AaC Plugin FIle

The AaC file containing the plugin definition.

### Code Output

The `--code-output` argument tells the generator the directory to put your generated code.  This will be the root of the package directory structure.

![Code Output Flag](../../images/examples/gen-plugin-code-output.png)

![Code Output Flag Directory Structure](../../images/examples/gen-plugin-output-code.png)

### Test Output

The `--test-output` argument tells the generator the directory to put your generated tests.  This will be the root of the test directory structure.

![Test Output Flag](../../images/examples/gen-plugin-test-output.png)

![Test Output Flag Directory Structure](../../images/examples/gen-plugin-output-test.png)

### Doc Output

The `--doc-output` argument tells the generator the directory to put your generated documentation.  _This is currently not used but may be in the future._

![Doc Output Flag](../../images/examples/gen-plugin-doc-output.png)

![Doc Output Flag Directory Structure](../../images/examples/gen-plugin-output-doc.png)

### No Prompt

The `--no-prompt` argument tells the generator to not ask the user to confirm the output directories.  This may be useful for CI/CD pipelines if you're generating plugin content automatically.

### Force Overwrite

The `--force-overwrite` argument tells the generator to overwrite all files (while still making a backup), rather than output `.aac_evaluate` files for user-editable files.

### Evaluate

The `--evaluate` argument tells the generator to only output `.aac_evaluate` files for all generated files, rather than overwriting them.

![Gen-Plugin Evaluate Terminal Output](../../images/examples/gen-plugin-evaluate-terminal.png)

![Gen-Plugin Evaluate Directory Structure Output](../../images/examples/gen-plugin-evaluate-output.png)

## Help

![Gen-Plugin Command Help](../../images/examples/gen-plugin-h.png)

## Gen-Project Command

Generate code and stubs for an AaC project.  Overwrites will backup existing files.

![Gen-Project Terminal Output](../../images/examples/gen-project-terminal-output.png)

![Gen-Project File Output](../../images/examples/gen-project-file-output.png)

## Optional Arguments

### AaC Plugin FIle

The AaC file containing the plugin definition.

### Output

The `--output` argument tells the generator the directory to put your generated project code.

![Output Flag Terminal Output](../../images/examples/gen-project-output-flag-terminal.png)

![Output Flag Directory Structure Output](../../images/examples/gen-project-output-flag-directory.png)

### No Prompt

The `--no-prompt` argument tells the generator to not ask the user to confirm the output directories.  This may be useful for CI/CD pipelines if you're generating plugin content automatically.

### Force Overwrite

The `--force-overwrite` argument tells the generator to overwrite all files (while still making a backup), rather than output `.aac_evaluate` files for user-editable files.

### Evaluate

The `--evaluate` argument tells the generator to only output `.aac_evaluate` files for all generated files, rather than overwriting them.

![Evaluate Terminal Output](../../images/examples/gen-project-evaluate-output-directory.png)

![Evaluate Directory Structure Output](../../images/examples/gen-project-evaluate-output-terminal.png)

## Help

![Gen-Project Command Help](../../images/examples/gen-project-h.png)
