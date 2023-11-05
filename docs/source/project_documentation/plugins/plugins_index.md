# AaC Plugins

AaC provides a plugin system to allow users to extend the capabilities of AaC. Plugins are Python packages that are installed alongside AaC and are loaded at runtime. Plugins can provide new capabilities to AaC, such as new data definitions, new commands, and new constraints.

You can extend AaC with your own plugins as described in the [Developer Guide](../dev_guide/dev_guide_index.md).

## Built-in Plugins

AaC comes with a number of built-in plugins that provide core capabilities. These plugins are installed as part of AaC and are loaded at runtime. The following plugins are currently available:

- [Version](version): Gives you the installed version of AaC.
- [Print Definitions](print_defs):  Prints the AaC definitions from the Language Context.  This is useful for debugging or may serve as a reminder of the definitions available.
- [Check](check): Runs the AaC constraints against a provided model.
- [Generate](generate):  Generic generation capability that can be used to generate any text file from a model.
- [Generate Plugin](gen_plugin):  A custom AaC generator to support the extension of AaC through plugin development.
