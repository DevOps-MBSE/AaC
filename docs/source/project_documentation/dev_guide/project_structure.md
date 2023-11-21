# Project Structure

## Python project

The backbone of AaC is the Python project which implements the underlying
functionality for AaC, as a whole.

### `cli` Package

Since AaC is built as a CLI-first tool in order to maintain a minimal footprint,
enable integration into CI/CD pipelines, etc, we require functionality for
allowing users to interact with the application via a command line. The `cli`
package provides this functionality for users including an internal
representation of AaC commands, translation between our internal structures and
the [click][1] CLI framework which we use for CLI interaction, etc.

Additionally, in the `cli.builtin_commands` package you will find AaC plugins
that provide functionality without which AaC could not operate effectively.

### `io` Package

As the name suggests, the `io` package provides functionality related to I/O
operations including parsing of AaC files.

### `lang` Package

The `lang` package provides the main programmatic interface for interacting with
AaC structures via the "Active Context" (which is an instance of a
`LanguageContext`). It also provides various utilities to enable working with
`Definition`s.

### `persistence` Package

At one point in time it was desirable to provide a level of persistence for the
`ActiveContext` so the `persistence` package was created to handle that.
Currently, however, it is being evaluated for deprecation in a future version since persistence is no longer meeting needs.

### `plugins` Package

At the heart of AaC's design philosophy is the desire to keep the core tool as
minimal as possible and allow for enhancing AaC functionality via plugins. To
balance this desire with the idea of providing enough additional functionality
to allow AaC to be useful "out-of-the-box", we use the `plugins` package.

The `plugins` package is similar to the `cli.builtin_commands` package except
for the fact that every plugin in the `plugins.first_party` package and every
validator in the `plugins.validators` (except for the `required_fields`
validator) could be deployed separately from the core AaC and the tool would
still work.

### `serialization` Package

We understand that not all AaC users will enjoy working from a terminal, so we've
also built an AaC LSP server that enables users to work from an editor or IDE.
To account for the need to run AaC commands from a non-CLI interface, we've
provided JSON serialization for AaC commands and their arguments. The
`serialization` package provides this functionality.

### `spec` Package

The `spec` package provides utilities for loading and interacting with the core
AaC specification. Additionally, the AaC DSL specification is defined in this
package.

### `templates` Package

Many AaC plugins generate output in some way. For anything more than simple
output, we leverage the [Jinja2][2] templating engine. The plumbing for
rendering templates and interacting with Jinja is contained in the `templates`
package.

### `validate` Package

A core feature of AaC is its extensibility and flexibility. As a result, a
plugin can contribute validations and the core AaC tool requires some way to
find them to execute against a given definition. The `validate` package is responsible
for validator discovery and application.

[1]: https://click.palletsprojects.com/en/
[2]: https://jinja.palletsprojects.com/en/
