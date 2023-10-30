# Generate Plugin

The `gen-plugin` plugin evaluates an AaC model against the AaC constraints.  The check plugin will output any errors that are found.

## Gen-Plugin Command

```bash
aac check my_model.aac
```

## Arguments

### AaC Plugin FIle

The AaC file containing the plugin definition.

### Code Output

The `--code-output` argument tells the generator the directory to put your generated code.  This will be the root of the package directory structure.

### Test Output

The `--test-output` argument tells the generator the directory to put your generated tests.  This will be the root of the test directory structure.

### Doc Output

The `--doc-output` argument tells the generator the directory to put your generated documentation.  This is currently not used but may be in the future.

### No Prompt

The `--no-prompt` argument tells the generator to not ask the user to confirm the output directories.  This may be useful for CI/CD pipelines if you're generating plugin content automatically.

### Force Overwrite

The `--force-overwrite` argument tells the generator to overwrite all files (while still making a backup), rather than output `.aac_evaluate` files for user-editable files.

### Evaluate

The `--evaluate` argument tells the generator to only output `.aac_evaluate` files for all generated files, rather than overwriting them.

## Help

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