"""Provide access to plugins and plugin data."""

from iteration_utilities import flatten
from pluggy import PluginManager

from aac import parser
from aac.lang.definitions.definition import Definition
from aac.plugins import hookspecs, PLUGIN_PROJECT_NAME
from aac.plugins.validators import ValidatorPlugin


def get_plugin_manager() -> PluginManager:
    """
    Gets the plugin manager and automatically registers internal plugins.

    Returns:
        The plugin manager.
    """
    # Import built-in commands
    from aac.cli.builtin_commands import (
        validate,
        version,
    )

    # Import plugins within the function to prevent circular imports and partial initialization
    from aac.plugins import (
        gen_json,
        gen_plugin,
        gen_protobuf,
        gen_design_doc,
        gen_gherkin_behaviors,
        gen_plant_uml,
        specifications,
        print_spec,
        start_lsp,
        help_dump,
        material_model,
    )

    # Import Validation Plugins
    from aac.plugins.validators import (
        defined_references,
        required_fields,
        validator_implementation,
        exclusive_fields,
        subcomponent_type,
    )

    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    # register "built-in" commands
    plugin_manager.register(validate)
    plugin_manager.register(version)

    # register "built-in" plugins
    plugin_manager.register(gen_json)
    plugin_manager.register(gen_plugin)
    plugin_manager.register(gen_protobuf)
    plugin_manager.register(gen_design_doc)
    plugin_manager.register(gen_gherkin_behaviors)
    plugin_manager.register(gen_plant_uml)
    plugin_manager.register(specifications)
    plugin_manager.register(print_spec)
    plugin_manager.register(start_lsp)
    plugin_manager.register(help_dump)
    plugin_manager.register(material_model)

    # register "built-in" validation plugins
    plugin_manager.register(defined_references)
    plugin_manager.register(required_fields)
    plugin_manager.register(validator_implementation)
    plugin_manager.register(exclusive_fields)
    plugin_manager.register(subcomponent_type)

    return plugin_manager


def get_plugin_definitions() -> list[Definition]:
    """
    Gets a list of all the plugin-defined AaC models and definitions.

    Returns:
        A list of parsed definitions from all active plugins.
    """
    plugin_manager = get_plugin_manager()
    plugin_definitions_as_yaml = plugin_manager.hook.get_plugin_aac_definitions()
    plugin_definitions = []
    for plugin_definition in plugin_definitions_as_yaml:
        if len(plugin_definition) > 0:
            plugin_definitions.append(parser.parse(plugin_definition))

    return list(flatten(plugin_definitions))


def get_validator_plugins() -> list[ValidatorPlugin]:
    """
    Gets a list of registered validator plugins and metadata.

    Returns:
        A list of validator plugins that are currently registered.
    """
    plugin_manager = get_plugin_manager()
    return plugin_manager.hook.register_validators()


def get_plugin_model_definitions() -> dict:
    """
    Gets all a list of all the plugin-defined AaC models and definitions.

    Returns:
        A list of plugin defined models.
    """
    plugin_manager = get_plugin_manager()
    plugin_models_yaml = plugin_manager.hook.get_plugin_aac_definitions()
    plugin_extensions = {}
    for plugin_ext in plugin_models_yaml:
        if len(plugin_ext) > 0:
            parsed_definitions = parser.parse(plugin_ext)
            definitions_dict = dict(map(lambda definition: (definition.name, definition.structure), parsed_definitions))
            plugin_extensions = definitions_dict | plugin_extensions

    return plugin_extensions
