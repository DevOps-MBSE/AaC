"""AaC Plugin implementation module for the gen_tmgrammar plugin."""

from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

plugin_name = "gen_tmgrammar"


def gen_tmgrammar(json: bool, plist: bool) -> PluginExecutionResult:
    """
    Generate a TextMate grammar for the AaC VSCode extension.

    Args:
        json (bool): Whether to generate the TextMate grammar as a JSON file.
        plist (bool): Whether to generate the TextMate grammar as a plist (XML) file.

    Returns:
        aac_textmate_grammar The TextMate Grammar that provides syntax rules for the AaC VSCode extension.
    """
    # TODO add implementation here
    def _implement_and_rename_me():
        raise NotImplementedError("gen_tmgrammar is not implemented.")

    with plugin_result(plugin_name, _implement_and_rename_me) as result:
        return result
