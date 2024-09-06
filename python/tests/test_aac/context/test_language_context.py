from unittest import TestCase

from aac.context.language_context import LanguageContext


class TestLanguageContext(TestCase):
    def test_LanguageContext(self):
        context_1 = LanguageContext()
        context_2 = LanguageContext()
        self.assertEqual(context_1, context_2)

    def test_get_aac_core_file_path(self):
        context = LanguageContext()
        self.assertIn("aac.aac", context.get_aac_core_file_path())

    def test_get_aac_core_as_yaml(self):
        context = LanguageContext()
        aac_yaml = context.get_aac_core_as_yaml()
        for definition in context.get_aac_core_definitions():
            self.assertIn(f"name: {definition.name}", aac_yaml)

    def test_parse_and_load(self):
        context = LanguageContext()
        definitions = context.parse_and_load(VALID_AAC_YAML_CONTENT)
        self.assertEqual(len(definitions), 1)
        self.assertIsNotNone(definitions[0].instance)
        self.assertEqual(definitions[0].name, "TestSchema")
        self.assertEqual(len(definitions[0].instance.fields), 4)

    def test_get_definitions(self):
        context = LanguageContext()
        definitions = context.get_definitions()
        # check a handful of the core definitions
        definition_names = [definition.name for definition in definitions]
        self.assertIn("Schema", definition_names)
        self.assertIn("Field", definition_names)
        self.assertIn("Primitive", definition_names)
        self.assertIn("Model", definition_names)

    def test_get_definitions_by_name(self):
        context = LanguageContext()
        definitions = context.get_definitions_by_name("Schema")
        self.assertEqual(len(definitions), 1)
        self.assertEqual(definitions[0].name, "Schema")
        self.assertIsNotNone(definitions[0].instance)

        context.parse_and_load(VALID_AAC_YAML_CONTENT_SPACE_IN_NAME)
        definitions = context.get_definitions_by_name("Test Schema2")
        self.assertEqual(definitions[0].name, "Test Schema2")

    def test_get_definitions_by_root(self):
        context = LanguageContext()
        definitions = context.get_definitions_by_root("schema")
        self.assertGreater(len(definitions), 1)
        definition_names = [definition.name for definition in definitions]
        self.assertIn("Schema", definition_names)

    def test_get_defining_schema_for_root(self):
        context = LanguageContext()
        definition = context.get_defining_schema_for_root("schema")
        self.assertEqual(definition.name, "Schema")

    def test_get_plugin_runners(self):
        context = LanguageContext()
        plugin_runners = context.get_plugin_runners()
        self.assertGreater(len(plugin_runners), 0)
        plugin_names = [runner.plugin_definition.name for runner in plugin_runners]
        self.assertIn("Version", plugin_names)

    def test_get_primitives(self):
        context = LanguageContext()
        primitives = context.get_primitives()
        primitive_names = [primitive.name for primitive in primitives]
        # check the core primitives
        self.assertIn("string", primitive_names)
        self.assertIn("int", primitive_names)
        self.assertIn("bool", primitive_names)
        self.assertIn("number", primitive_names)
        self.assertIn("any", primitive_names)
        self.assertIn("date", primitive_names)
        self.assertIn("file", primitive_names)
        self.assertIn("directory", primitive_names)
        self.assertIn("dataref", primitive_names)
        self.assertIn("typeref", primitive_names)

    def test_get_python_type_from_primitive(self):
        context = LanguageContext()
        self.assertEqual(context.get_python_type_from_primitive("string"), "str")
        self.assertEqual(context.get_python_type_from_primitive("int"), "int")
        self.assertEqual(context.get_python_type_from_primitive("bool"), "bool")
        self.assertEqual(context.get_python_type_from_primitive("number"), "float")

    def test_is_extension_of(self):
        context = LanguageContext()
        definition = context.get_definitions_by_name("Schema")
        self.assertTrue(context.is_extension_of(definition[0], "aac.lang", "AacType"))

    def test_get_definitions_of_type(self):
        context = LanguageContext()
        definitions = context.get_definitions_of_type("aac.lang", "AacType")
        self.assertGreater(len(definitions), 1)

    def test_get_values_by_field_chain(self):
        context = LanguageContext()
        test_values = ["schema.fields.name", "enum.values", "primitive.python_type"]
        for val in test_values:
            values = context.get_values_by_field_chain(val)
            self.assertGreater(len(values), 1)

VALID_AAC_YAML_CONTENT = """
schema:
  name: TestSchema
  description: |
    This is a test schema.
  fields:
    - name: string_field
      type: string
      description: |
        This is a test field.
    - name: integer_field
      type: integer
      description: |
        This is a test field.
    - name: boolean_field
      type: boolean
      description: |
        This is a test field.
    - name: number_field
      type: number
      description: |
        This is a test field.
""".strip()

VALID_AAC_YAML_CONTENT_SPACE_IN_NAME = """
schema:
  name: Test Schema2
  description: |
    This is a test schema.
  fields:
    - name: string_field
      type: string
      description: |
        This is a test field.
    - name: integer_field
      type: integer
      description: |
        This is a test field.
    - name: boolean_field
      type: boolean
      description: |
        This is a test field.
    - name: number_field
      type: number
      description: |
        This is a test field.
""".strip()
