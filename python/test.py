from aac.context.language_context import LanguageContext
from aac.context.definition_parser import DefinitionParser
from aac.in_out.parser import parse, ParserError


def test_tokens(definition):
    context = LanguageContext()
    context.parse_and_load(definition)

YAML = """
model:
    name: Name
    description: yes
"""

test_tokens(YAML)
