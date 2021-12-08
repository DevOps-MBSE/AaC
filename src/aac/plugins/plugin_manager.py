from pluggy import PluginManager


def get_plugin_manager() -> PluginManager:
    """
    Gets the plugin manager and automatically registers internal plugins.

    Returns:
        The plugin manager.
    """
    from aac import genjson
    from aac.plugins import hookspecs, PLUGIN_PROJECT_NAME
    from aac.plugins import (
        gen_plugin,
        gen_protobuf,
        gen_design_doc,
        gen_gherkin_behaviors,
        gen_plant_uml,
        specifications,
    )

    plugin_manager = PluginManager(PLUGIN_PROJECT_NAME)
    plugin_manager.add_hookspecs(hookspecs)
    plugin_manager.load_setuptools_entrypoints(PLUGIN_PROJECT_NAME)

    # register "built-in" plugins
    plugin_manager.register(genjson)
    plugin_manager.register(gen_plugin)
    plugin_manager.register(gen_protobuf)
    plugin_manager.register(gen_design_doc)
    plugin_manager.register(gen_gherkin_behaviors)
    plugin_manager.register(gen_plant_uml)
    plugin_manager.register(specifications)

    return plugin_manager


def get_plugin_model_definitions():
    """
    Gets all a list of all the plugin-defined AaC models and definitions.

    Returns:
        A list of plugin defined models.
    """
    from aac import parser

    plugin_manager = get_plugin_manager()
    plugin_models_yaml = plugin_manager.hook.get_base_model_extensions()
    plugin_extensions = {}
    for plugin_ext in plugin_models_yaml:
        if len(plugin_ext) > 0:
            models = parser.parse_str(plugin_ext, "Plugin Manager Addition", False)
            plugin_extensions = models | plugin_extensions

    return plugin_extensions
