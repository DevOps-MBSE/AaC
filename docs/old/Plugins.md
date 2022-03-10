# Plugins

## Registering Plugins
Currently, plugins are loaded by checking for packages with `setup.py` entrypoints that match the group name defined in the AaC package ("aac").

Example `setup.py`
```python
from setuptools import setup

setup(
    version="0.0.1",
    name="aac-echo-simple",
    install_requires=["aac"],
    entry_points={
        "aac": ["aac-echo-simple=simple"],
    },
)
```

In the above example, the `entry_points` can be broken down into the following structure.
```python
    entry_points={
        "<group>": ["<name>=<impl_module>"],
    },
```

Currently, the _only_ requirement is that the plugin specify a value in the `<group>` that matches the group identifier defined in the plugin manager ("aac").

## Local Development
If you're developing plugins locally in the top-level plugins directory then you will need to locally install them with pip and with the `--editable,-e` flag:
```bash
cd plugins/aac-my-plugin/ #Or whatever your plugin directory is
pip install -e . # -e for editable
```
Once the plugin packages have been installed, then the plugin manager in AaC will be able to pick them up and import them.

## Validating AaC Models in a Plugin

To validate an Architecture-as-Code model from within your plugin, you can do the following:

```python
from pprint import pprint

from aac.parser import parse
from aac.plugins.plugin_execution import plugin_result
from aac.validator import validation

def my_plugin_command(architecture_file: str):
    def cmd():
        with validation(parse, architecture_file) as result:
            # Do whatever you want to with the validated `model' here.
            pprint(result.model)
            return f"The model in {architecture_file} is valid!\n"

    with plugin_result('my-plugin-name', cmd) as result:
        return result
```

It's worth noting that the context manager will yield `None` if the model is invalid so the standard pattern we use to handle this is, for example, `if not model: something()`, where `something()` is your procedure for dealing with an invalid model.

## Pitfalls
Some pitfalls experienced when implementing the example echo plugins.

### Multiple Plugin Module name collision
If more than plugin uses the same name for a module, it will create runtime errors when loading multiple plugins that have the same module name.

For example, if we have two plugins that implement the `echo()` spec, and the two modules define their `echo()` implemenetations in modules that happen to share the same name `echo.py`, then the plugin manager will fail when loading in the second plugin.

If we were to change the module name from `echo.py` in one of our plugins, then we'll be able to successfully load in both plugins.

### Inter-package module name collision
If your plugin is mysteriously not being executed despite being loaded by the plugin manager, it's possible that there is a naming collision preventing the plugin from being executed correctly. This exact scenario occured when the project contained a module `aac.echo` that was colliding with a plugin module that was also named `echo`. The exact conflict wasn't determined, but changing the plugin's module from `echo` to something else (`simple`) overcame the module name collision.