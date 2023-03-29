"""AaC Plugin implementation module for the gen_tmgrammar plugin."""

from aac.plugins.plugin_execution import PluginExecutionResult, plugin_result

plugin_name = "gen_tmgrammar"

BASE_SYNTAX_FILE_NAME = "aac-syntax"
JSON_SYNTAX_FILE_NAME = f"{BASE_SYNTAX_FILE_NAME}.json"
PLIST_SYNTAX_FILE_NAME = f"{BASE_SYNTAX_FILE_NAME}.plist"


def gen_tmgrammar(json: bool = True, plist: bool = False) -> PluginExecutionResult:
    """
    Generate a TextMate grammar for the AaC VSCode extension.

    Args:
        json (bool): Whether to generate the TextMate grammar as a JSON file.
        plist (bool): Whether to generate the TextMate grammar as a plist (XML) file.

    Returns:
        aac_textmate_grammar The TextMate Grammar that provides syntax rules for the AaC VSCode extension.
    """

    def write_textmate_grammar_to_file(file_name: str) -> str:
        with open(file_name, "w"):
            pass

        return f"{file_name} created successfully."

    with plugin_result(
        plugin_name,
        write_textmate_grammar_to_file,
        JSON_SYNTAX_FILE_NAME if json else PLIST_SYNTAX_FILE_NAME,
    ) as result:
        return result
