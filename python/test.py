from aac.context.language_context import LanguageContext
from aac.context.definition_parser import DefinitionParser
from aac.in_out.parser import parse, ParserError
from aac.context.language_error import LanguageError
from aac.context.lexeme import Lexeme

def test_tokens(definition):
    # lex = Lexeme()
    # print(lex)
    context = LanguageContext()
    definition = context.parse_and_load("./test.aac")
    # print(definition)
    raise LanguageError(
        message="not shown",
        location="not shown"
        )

    raise LanguageError(
        "shown",
        "shown",
        )


YAML = """
schema:
    name: Name
    description: yes
"""

test_tokens(YAML)
