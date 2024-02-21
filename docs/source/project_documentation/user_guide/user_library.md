# User Libraries
Because of the extensibility and reusability goals of AaC, a plugin can also be designed as a library for a project. By making a plugin to function more as a library, it exposes itself as a tool to be utilized in a larger context throughout the AaC space.

## Contributing Definitions to a User Library
One of the primary contributions that AaC plugins provide are sets of AaC definitions that can be leveraged by users in their modeled systems. For instance, an organization may have a common set of model components that they wish to share amongst teams as an internal library. AaC plugins provide users with a distributable, immutable set of definitions that can also be distributed alongside the AaC tool via the pip package manager tool.

To understand more about definitions and their role in AaC, see the [Definitions](#definitions) section of the AaC Modeling Language Reference page.

While AaC plugins aren't limited to only contributing definitions, this is the only plugin functionality necessary to create a distributable user library for the AaC tool. In order to support user libraries, plugins include their definitions as part of their registration in AaC. For references on how to register an AaC plugin, see [Plugin Developer Guide](../dev_guide/plugin_dev_guide)

## Contributing Root Keys to a User Library
AaC uses a set of root-level keys to define instances of modeled 'things' that are defined data structures (schemas). An example is the root key `schema`, which defines an instance of a data structure that can be referenced. The core AaC definitions have several root keys, but users are capable of defining custom root keys.  Custom root keys allow users to define instances of models or modeled components.

## Note to Plugin Developers
Currently AaC does not have a plugin system capable of defining dependencies across plugins. If a plugin implements a User Library (another plugin), the onus of managing dependencies and versions rests entirely on the users and developers. There is future functionality to address these shortcomings. For now, clear communication, documentation, and dependency files (e.g. requirements.txt, poetry.lock, setup.py, etc) are the best way to mitigate dependency issues.
