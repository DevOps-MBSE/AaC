# AaC Constraints
## What is Constraint Checking in the AaC Language?
Because the AaC DSL is leveraging plain-text YAML, there is little to no YAML functionality to guide users in the correctness of their AaC structures. AaC makes use of a self-checking language feature so that users can reference which rules are applied to which AaC DSL components, and so that users can define constraints for their own user-defined structures. To this end, AaC employs a plugin-based constraint system where plugins provide Python-based constraint implementations that can be referenced and applied to definitions in the AaC DSL.

Constraint rules in AaC are defined with the `context_constraint`, `schema_constraint`, and `primitive_constraint` definitions, which are required to have a corresponding implementation, via an AaC plugin. This enables AaC's self-checking mechanism even though YAML is just a markup language.

### Checking an AaC File
The overall constraint mechanism follows this flow:
1. An AaC file needs to be checked (i.e. you run `aac check <AaC_file_path>`)
2. Certain "core" language checks must be performed while parsing and loading the AaC definition.
  a. This includes items such as required fields being present, fields being recognized based on their defining schema, etc.
3. Context constraints will be checked
  a. A context constraint is a "global" language constraint, or an "invariant".  These constraints apply checks to the collection of definitions in the AaC `LanguageContext`.
4. Each parsed definition will be checked against assigned schema constraints
  a. Declare relevant schema constraints within the schema definition.  Schema constraints may accept arguments.
  b. In certain cases, you may need to define a `universal` schema constraint.  These are applied to all schema definitions without the need for an explicit declaration.  Universal schema constraints cannot be defined with arguments.
5. As schemas are checked against constraints, all fields and sub-fields are evaluated individually throughout the declaration structure.
6. When traversing the declaration structure of a definition, if primitive values are encountered they are checked against any defined primitive constraints for that primitive.
  a. Primitive constraints are declared within the primitive declaration, not at the point of usage.
7. Once all of the parsed declarations are checked against declared constraints, any violations are reported as constraint errors.
8. All constraint errors from all of the constraint rules are collected and returned together.
  a. If there are no errors, the user is provided a success message
  b. If there are errors, the AaC file fails the check.  There is an option on the `check` command to handle warnings as errors if desired.

![Constraint Check Flow Chart](../../images/graphs/constraint_flow.png)

## Constraint Definitions
In order to define the constraints used by the AaC DSL to check the correctness of a definition, you must declare constraint rules via the 3 types of constraint definitions. These definitions also provide contextual information for the constraint as well as behaviors and acceptance criteria -- something to leverage for automatically generating functional/integration tests in the future.

### Generation File Safety

If you need to update your plugin declaration, you can re-run `gen-plugin` without concern of losing any prior work.  If the output python files already exist, the generator will produce:

  - `.aac_evaluate` files for any user-editable output with an already existing file.  You can look at the changes here and incorporate into your content.
  - `.aac_backup` files for non-user editable output with an already existing file.  The backup contains the pre-existing content for your review.

Once you're satisfied, run `aac clean <path_to_AaC_plugin_file> --code-output <src_path> --test-output <tests_path>` to remove any `.aac_evaluate` and `.aac_backup` files.

Currently we are not generating documentation for plugins...so you're on your own for that.  Hopefully we'll get some content generation in place in the future to simplify plugin document content management.

### Context Constraints
Here is an example `context_constraint` definition:

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/unique_root_keys/unique_root_keys.aac
    :language: yaml
```

To implement the context constraint, run `aac gen-plugin <path-to-unique_root_keys.aac> --code-output <src-path> --test-output <tests-path>`.  Note that the package declaration will be used to establish sub-directories under your `--code-output` and `--test-output` paths.  By default, the `gen-plugin` command will prompt you to confirm the target output paths prior to attempting to generate any files.

The `gen-plugin` command will auto-generate all the boilerplate Python code to integrate your new command into the AaC plugin framework and will provide you an implementation stub to populate. It will also generate feature files and a unit test file based on your declaration. This particular example does not demonstrate the use of feature files.

Generated implementation stub:
```python
"""The AaC Unique Root Keys plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

# There may be some unused imports depending on the definition of the plugin...but that's ok
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)

from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.context.source_location import SourceLocation
from typing import Any


plugin_name = "Unique Root Keys"


def root_key_names_are_unique(context: LanguageContext) -> ExecutionResult:
    """Business logic for the Root key names are unique constraint."""

    # TODO: rewrite the code below to implement your constraint logic
    # you will likely be evaluating definitions from the LanguageContext, so use the source and location from the definition for messages
    status = ExecutionStatus.GENERAL_FAILURE
    messages: list[ExecutionMessage] = []
    error_msg = ExecutionMessage(
        "The Root key names are unique constraint for the Unique Root Keys plugin has not been implemented yet.",
        MessageLevel.ERROR,
        None,
        None,
    )
    messages.append(error_msg)

    return ExecutionResult(plugin_name, "Root key names are unique", status, messages)
```

Generated unit test:
```python
from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus


from aac.plugins.unique_root_keys.unique_root_keys_impl import plugin_name


from aac.plugins.unique_root_keys.unique_root_keys_impl import root_key_names_are_unique


class TestUniqueRootKeys(TestCase):
    def test_root_key_names_are_unique(self):
        # TODO: Write tests for root_key_names_are_unique
        self.fail("Test not yet implemented.")

```

To complete the implementation of a constraint, replace the body of the stubbed unit test and implementation with the desired behavior.  Use the provided `context` as the "item under evaluation" and return an `ExecutionResult` with the appropriate status and messages as shown in the generated example.



Once the constraint implementation and unit test(s) are completed, run `tox` to ensure everything passes.

### Schema Constraints

Here's an example `schema_constraint` definition.

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/exclusive_fields/exclusive_fields.aac
    :language: yaml
```

Just as in the context constraint example, run `gen-plugin` to create the implementation and unit test stubs.  Note that this is not a universal schema constraint, so arguments are allowed in the declaration.  If this were a universal constraint (i.e. `universal: true`), then `gen-plugin` would fail due to violation of the `If true then empty` constraint declared for `SchemaConstraint` in th AaC core language definition.

Generated implementation stub:

```python
"""The AaC Exclusive fields plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

# There may be some unused imports depending on the definition of the plugin...but that's ok
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)

from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.context.source_location import SourceLocation
from typing import Any


plugin_name = "Exclusive fields"


def mutually_exclusive_fields(
    instance: Any, definition: Definition, defining_schema, fields
) -> ExecutionResult:
    """Business logic for the Mutually exclusive fields constraint."""

    # TODO: rewrite the code below to implement your constraint logic
    # you can get the source and location from the definition for messages
    status = ExecutionStatus.GENERAL_FAILURE
    messages: list[ExecutionMessage] = []
    error_msg = ExecutionMessage(
        "The Mutually exclusive fields constraint for the Exclusive fields plugin has not been implemented yet.",
        MessageLevel.ERROR,
        definition.source,
        None,
    )
    messages.append(error_msg)

    return ExecutionResult(plugin_name, "Mutually exclusive fields", status, messages)

```

Generated test stub:
```python
from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus


from aac.plugins.exclusive_fields.exclusive_fields_impl import plugin_name


from aac.plugins.exclusive_fields.exclusive_fields_impl import mutually_exclusive_fields


class TestExclusivefields(TestCase):
    def test_mutually_exclusive_fields(self):
        # TODO: Write tests for mutually_exclusive_fields
        self.fail("Test not yet implemented.")
```

Since this is not a context constraint (i.e. applicable globally across the AaC Language Context), you must declare it where appropriate.  There's not a current example of the "Mutually Exclusive" constraint in the current AaC baseline, so let's switch over to the "If true then empty" constraint to see how schema constraints are allocated.  In this example, the constraint is used to check the boolean value of the `universal` field and if true, ensure there are no values provided for the `arguments` field.  Everything described above for plugin-generation applies here as well.  What we really want to focus on is the assignment of the schema constraint, including the arguments provided for the constraint.


```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 1025-1065
    :emphasize-lines: 35-41
```

Now write the test and implementation for the constraint. Remember to run `aac clean` to remove any extra files, if needed.

### Primitive Constraints

The core AaC DSL defines a handful of common primitives such as `int` and `string` for you to use, but also allows you to define custom primitives as needed for your modeling needs.  In order to show how this can be done, consider an AaC unique primitive: `dataref`.

First, define the `dataref` primitive without any declared constraints.

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 173-182
```

Now that we have something to work with, we can define a primitive constraint.

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/plugins/aac_primitives/aac_primitive_constraints.aac
    :language: yaml
    :lines: 1-6, 21-22
    :emphasize-lines: 7-8
```

Just as before, run `gen-plugin` to create unit test and implementation stubs.

Generated implementation stub:

```python
"""The AaC AaC primitive constraints plugin implementation module."""
# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

# There may be some unused imports depending on the definition of the plugin...but that's ok
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)

from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.context.source_location import SourceLocation
from typing import Any


plugin_name = "AaC primitive constraints"


def check_dataref(
    value: str, type_declaration: str, source: AaCFile, location: SourceLocation
) -> ExecutionResult:
    """Business logic for the Check dataref constraint."""

    # TODO: rewrite the code below to implement your constraint logic
    # the checker has provided you with source and location data for messages
    status = ExecutionStatus.GENERAL_FAILURE
    messages: list[ExecutionMessage] = []
    error_msg = ExecutionMessage(
        message="The Check dataref constraint for the AaC primitive constraints plugin has not been implemented yet.",
        level=MessageLevel.ERROR,
        source=source,
        location=location,
    )
    messages.append(error_msg)

    return ExecutionResult(plugin_name, "Check dataref", status, messages)

```

Generated unit test stub:

```python
from unittest import TestCase
from typing import Tuple
from click.testing import CliRunner
from aac.execute.command_line import cli, initialize_cli
from aac.execute.aac_execution_result import ExecutionStatus


from aac.plugins.aac_primitives.aac_primitive_constraints_impl import plugin_name

from aac.plugins.aac_primitives.aac_primitive_constraints_impl import check_dataref


class TestAaCprimitiveconstraints(TestCase):
    def test_check_dataref(self):
        # TODO: Write tests for check_dataref
        self.fail("Test not yet implemented.")

```

You may now create your primitive constraint test and implementation.  Remember to add an empty `__init__.py` to your test directory and run `aac clean` to remove any extra files if needed.

Finally, be sure to assign the primitive constraint you've created to your primitive declaration.

```{eval-rst}
.. literalinclude:: ../../../../python/src/aac/aac.aac
    :language: yaml
    :lines: 173-184
```

## Conclusion

AaC attempts to provide the flexibility needed to create custom models for your engineering domain, and the constraint definition capabilities to support your unique needs. We've provided the constraints required to allow AaC to define and check itself. These constraints should provide sound examples for you to use when building your own constraints.  Over time, new constraints will be provided. Feel free to use / reuse the core AaC constraints in your model definitions as needed.
