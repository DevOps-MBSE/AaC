# AaC Definitions

AaC is a model-based system engineering (MBSE) tool that allows you to declare your models in text (YAML) rather than using a database like other MBSE tools.  This allows you more rigorous baseline control in parallel with your collaborators with  better version control of your models.  In AaC, we refer to each portion of YAML you declare as a `Definition`.  In short, a `Definition` is anything with a root YAML key, whether it is defined in a single file or aggregated with other YAML using the `---` YAML separator.

## Parsing and Loading

When you parse an AaC file by using `parse` from `aac.in_out.parser._parse_source`, you get a list of `Definition` objects; assuming no `ParserError` exception is encountered.  Parsing an AaC file does not load the content into the `LanguageContext`.  To properly load the AaC file content you can provide the parsed definitions to the LanguageContext load file by using `load_definitions` from `aac.context.LanguageContext`. But perhaps the simpler way is to just use the `parse_and_load` function on the `LanguageContext` which combines everything into a single call.

If you're building a custom plugin, you'll almost certainly parse and load an AaC file and then want to do something with the resulting `Definition` objects.  We recommend you use the `LanguageContext.parse_and_load` function and then use the `instance` variable within the resulting `Definition` objects to perform your work.  Here is an example of how you can use the `LanguageContext` to get a list of `Definition` objects from an AaC file in a fictional plugin function.

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
- `name (str)`: The name of the definition.
- `package (str)`: The package of the definition.
- `content (str)`: The original textual representation of the definition.
- `source (AaCFile)`: The source document containing the definition.
- `lexemes (list[Lexeme])`: A list of lexemes for each item in the parsed definition.
- `structure (dict)`: The dictionary representation of the definition.
- `instance (Any)`: An AaC Python object representing the parsed definition.

_It is important to note that parsing populates everything in the `Definition` except for the `instance` field.  The `instance` field is only populated when the `Definition` is loaded into the `LanguageContext`.`_

In AaC, every `Definition` has a `name` field which is generally used to refer to or select it. `Definition` objects also have a `package` field which can be used in combination with the `name` field to identify that `Definition`. If no package is defined, a default value of `default` is used. If you're creating a new root model type, you must ensure your `schema` includes a `name` field at a minimum to support the loading of any `Definition` defined with that root key. Internally, this is used to generate a dynamic Python class which is used as the value of the `Definition.instance` field.

The `instance` variable is intended to provide a simple way for you to interact with AaC data.  This is new to AaC since version `0.4.0` and provides you a more streamlined way to work with your data than the `structure` dictionary.  Let's say you've got a relatively complex schema definition with a series of nested fields, and you need a data item.  Here's an hypothetical example of how you can access such a data item if you've defined a custom acceptance test root definition.

Example acceptance test AaC definition:
```{eval-rst}
.. literalinclude:: ../../../../python/features/docs_examples/dev_guide_language_api_definitions/acceptance_test.aac
    :language: yaml
```

```python
# we've already run parse_and_load and now want to find the acceptance test items
context = LanguageContext()
definitions = context.parse_and_load("acceptance_test.aac")
for definition in context.get_definitions_by_root("acceptance_test"):
    acceptance_test = definition.instance
    test_name = acceptance_test.name
    for scenario in acceptance_test.scenarios
        print(f"Acceptance Test '{test_name}' contains a scenario called '{scenario.name}'")
```

By using the instance variable, you can you use standard Python object navigation to work with your AaC data.  That said, there's nothing stopping you from working with the dictionary in the `structure` variable if you prefer, but we've found this significantly increases the complexity and time needed to create AaC functionality.
