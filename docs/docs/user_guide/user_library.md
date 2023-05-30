---
layout: default
title: Creating a User Library
parent: User's Guide to AaC
nav_order: 3
permalink: docs/user_guide/user_library
---
# Contributing Definitions to a User Library
One of the primary contributions that AaC plugins provide are sets of AaC definitions that can be leveraged by users in their modeled systems. For instance, an organization may have a common set of model components that they wish to share amongst teams as an internal library. AaC plugins provide users with a distributable, immutable set of definitions that can also be distributed alongside the AaC tool via the pip package manager tool.

To understand more about definitions and their role in AaC, see the [Definitions](./aac_language/#definitions) section of the AaC Modeling Language Reference page.

While AaC plugins aren't limited to only contributing definitions, this is the only plugin functionality necessary to create a distributable user library for the AaC tool. In order to support user libraries, plugins include their definitions as part of their registration in AaC. For references on how to register an AaC plugin, see [Plugins](../../old/Plugins) and [Plugin Developer Guide](../dev_guide/plugin_dev_guide)

## Inactive User Library Plugin
When a plugin has definitions associated with it, but the plugin has not been activated, the definitions are not available for use by AaC. To confirm a plugin has been installed, but not registered, run the following command: `aac --inactive`.

![Inactive Plugins](../../../assets/images/user_library/inactive_plugins.png)
## Active User Library Plugin
In order to use the definitions in a user library plugin, you must make sure that it is actively contributing definitions to the context.

You can activate a registered plugin by using the following command: `aac activate-plugin <plugin name>`.

![Activate Command](../../../assets/images/user_library/activate_command.png)

Verify the plugin has been activated by running the following command: `aac --active`

![List Active](../../../assets/images/user_library/list_active.png)

Once you have verified that your plugin has been activated, you are able begin referencing the definitions in your plugin. If you get validation errors about undefined types, double check that your plugin is listed as actively installed.

To demonstrate this behavior, take this example aac file:
```yaml
schema:
    name: ProtobufTypeExample
    fields:
        - name: int64Field
          type: int64
          description: This field references a primitive type provided by Gen-Protobuf
```

It references a type `int64` provided by the plugin `gen-protobuf`. If we validate this file with the plugin active, it'll successfully validate.
![Validate example](../../../assets/images/user_library/validate_example.png)

If we deactivate `gen-protobuf` and run the validation again, we'll see an error indicating our plugin type isn't defined.

![Revalidate example](../../../assets/images/user_library/revalidate_example.png)

Once you have verified that your plugin has been activated, you are able to check what plugin definitions, plugin commands, and such are available by running these commands: `aac <plugin name> --definitions` *think this is the correct command, please correct if not*

`<include screen shot of list results of plugin definitions>`

`aac <plugin name> --commands` *think this is the correct command, please correct if not*

`<include screen shot of list results of plugin commands>`

# Contributing Root Keys to a User Library
AaC uses a set of root-level keys to define instances of modeled 'things' that are defined data structures (schemas) within AaC. A quick example is that the root key `schema` defines an instance of a data structure that can be referenced. Custom root keys allow users to define instances of models or modeled components. The core AaC specification has several root keys, but users are capable of defining their own root keys. For more information on pre-defined Root Keys, see the [Root Keys](./aac_language/#root-keys) section of the AaC Modeling Language Reference page.

## Defining, adding, and leveraging a Root Key
Due to AaC's self-defining design, users must extend the `root` definition because each field is a mapping of a root key to its defined structure. See [Definition Extensions](../advanced_user_topics/language_extensions.md) for more information on extending definitions in AaC.
There is information about how the core spec is utilized as well as information and an example of how to extend the DSL for use via an additional plugin within the [Base DSL and Extended DSL](./aac_language/#the-base-dsl-core-spec) sections of the AaC Modeling Language Reference page.

In order to have your plugin provide custom root keys, it must have an extension targeting the `root` definition. This extension will need to be a `schemaExt` given that `root` is a schema definition. This extension will add additional fields to the `root` definition; each field in the `root` definition defines a root key and its corresponding data structure in the AaC language. Depending on the user library and what kind of items its modeling, user library key roots can be used to define instance of any modeled things such as cars, furniture, electronic networks, cloud networks, etc. Be aware that other plugins that aren't intentionally built to process the data modeled in your user library will likely be incompatible with any new root keys and data structures and can lead to incomplete generated artifacts.

# Note to Plugin Developers
At the moment, AaC does not have a plugin system capable of supporting defining dependencies amongst on other plugins. If your plugin implements a user library (another plugin), the onus of managing dependencies and versions rests entirely on the users and yourself. There is future functionality to address these shortcomings, but for now clear comunication, documentation, and dependency files (e.g. requirements.txt, poetry.lock, setup.py, etc) are the best way to mitigate issues.
