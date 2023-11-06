---
layout: default
parent: Language API
title: AaC Definitions
nav_order: 3
has_children: false
---
# AaC Definitions

AaC is a model-based system engineering (MBSE) tool that allows you to declare your models in text (YAML) rather than using a database like other MBSE tools.  This allows you to much more rigorous work in parallel with your collaborators with much better version control of your models.  In AaC, we refer to each portion of YAML you declare as a `Declaration`.  In short, a declaration is anything with a root YAML key, whether it is defined in a single file or aggregated with other YAML using the `---` YAML separator.

## Parsing and Loading

When you parse an AaC file (using `from aac.in_out.parser._parse_source import parse`), you get a list of `Definition` objects...assuming no `ParserError` exception is encountered.  Parsing an AaC file does not load the content into the `LanguageContext`.  To properly load the AaC file content you can provide the parsed definitions to the LanguageContext load file (using `from aac.context.LanguageContext in port load_definitions`). But perhaps the simpler way is to just use the `parse_and_load` function on the `LanguageContext` which combines everything into a single call.

If you're building a custom plugin, you'll almost certainly parse and load an AaC file and then want to do something with the resulting definitions.  We recommend you use  `LanguageContext.parse_and_load` function and then use the instance variable within the resulting Definitions to perform your work.  Here's an example of how you can use the `LanguageContext` to get a list of definitions from an AaC file in a fictional plugin function.

```python
def my_plugin_function(aac_file: str) -> ExecutionResult

    context = LanguageContext()
    definitions = context.parse_and_load(aac_file)
    for definition in definitions:
        # TODO:  Do something with the parsed definition
        pass

```

## Using Definition

Each `Definition` contains the following data:

- `uid (UUID)`: A unique identifier for selecting the specific definition.
- `name (str)`: The name of the definition
- `package (str)`: The package of the definition
- `content (str)`: The original source textual representation of the definition.
- `source (AaCFile)`: The source document containing the definition.
- `lexemes (list[Lexeme])`: A list of lexemes for each item in the parsed definition.
- `structure (dict)`: The dictionary representation of the definition.
- `instance (Any)`: An AaC python object representing the parsed definition.

It is important to note that parsing populates everythign in the `Definition` except for the `instance`.  The `instance` field is only populated when the `Definition` is loaded into the `LanguageContext`.`

AaC generally uses the `name` of the definition to refer to it, but also frequently augment that with the `package` to create a fully qualified name.  If there is no package, a default value of `default` is used.  The two portions of the definition you're most likely to use are the structure (the dictionary output from parsing the YAML) or the instance (an AaC auto-generated python object).  If you're creating a new root model type, you must ensure your `Schema` includes a `name` field at a minimum to support this convention.

The `instance` variable is intended to provide a simple way for you to interact with AaC data.  This is new to AaC since version `0.4.0` and provides you a more streamlined way to work with your data than the `structure` dictionary.  Let's say you've got a relatively complex schema definition with a series of nested fileds and you need a data item.  Here's an hypothetical example of how you can access such a data item if you've defined a custom acceptance test root definition.

Example acceptance test AaC definition:
```yaml
schema:
  name: AcceptanceTest
  package: aac.example
  root: acceptance_test
  fields:
    - name: name
      type: string
    - name: scenarios
      type: AcceptanceTestScenario[]
---
schema:
  name: AcceptanceTestScenario
  package: aac.example
  fields:
    - name: name
      type: string
```

```python
# we've already run parse_and_load and now want to find the acceptance test items
context = LanguageContext
for definition in context.get_definitions_by_root("acceptance_test"):
    acceptance_test = dictionary.instance
    test_name = acceptance_test.name
    for scenario in acceptance_test.scenarios
        print(f"Acceptance Test '{test_name}' contains a secnario called '{scenario.name}'")
```

By using the instance variable, you can you use standard python to work with your AaC data.  That said, there's nothing stopping you from working with the dictionary in the struture variable if you prefer, but we've found this significantly increases the complexity and time needed to create AaC functionallity.
