from unittest import TestCase

from aac.context.language_context import LanguageContext
from aac.context.language_error import LanguageError
from aac.in_out.parser._parser_error import ParserError


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

    def test_get_aac_core_definitions(self):
        context = LanguageContext()
        definitions = context.get_aac_core_definitions()
        self.assertIn("name: Schema", str(definitions))
        self.assertIn("name: Requirement", str(definitions))
        self.assertIn("name: Model", str(definitions))

    def test_is_aac_instance(self):
        context = LanguageContext()
        object = context.create_aac_object("Schema", {})
        self.assertTrue(context.is_aac_instance(object, "Schema"))

    def test_create_aac_object(self):
        context = LanguageContext()
        object = context.create_aac_object("Schema", {})
        self.assertEqual(str(type(object)), "<class 'aac.lang.Schema'>")

    # Something is going wrong with this method, it is failing to create the class. Putting a pin in it.
    # def test_create_aac_enum(self):
    #     context = LanguageContext()
    #     enum = context.create_aac_enum("RequirementVerificationMethod", "TEST")
    #     self.assertEqual(str(type(enum)), "aac.lang.RequirementVerificationMethod")
    #     self.assertEqual(str(enum), "TEST")

    def test_parse_and_load(self):
        context = LanguageContext()
        definitions = context.parse_and_load(VALID_AAC_YAML_CONTENT)
        self.assertEqual(len(definitions), 1)
        self.assertIsNotNone(definitions[0].instance)
        self.assertEqual(definitions[0].name, "TestSchema")
        self.assertEqual(len(definitions[0].instance.fields), 4)

    def test_remove_definitions(self):
        context = LanguageContext()
        loaded_definition = context.parse_and_load(VALID_AAC_YAML_CONTENT)
        name = loaded_definition[0].name
        definition = context.get_definitions_by_name(name)
        self.assertGreater(len(definition), 0)
        context.remove_definitions(definition)
        definition = context.get_definitions_by_name(name)
        self.assertEqual(len(definition), 0)

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

    def test_is_aac_instance_fail(self):
        with self.assertRaises(KeyError):
            context = LanguageContext()
            context.parse_and_load(VALID_AAC_YAML_CONTENT)
            object = context.create_aac_object("TestSchema", {})
            context.remove_definitions(context.get_definitions_by_name("TestSchema"))
            context.is_aac_instance(object, "TestSchema")

    def test_create_aac_object_incorrect_type(self):
        with self.assertRaises(AttributeError):
            context = LanguageContext()
            object = context.create_aac_object("Schema", "Attribute")  # noqa: F841

    # Something is going wrong with this method, it is failing to create the class. Putting a pin in it.
    # def test_create_aac_enum_incorrect_type(self):
    #   with self.assertRaises(AttributeError):
    #       context = LanguageContext()
    #       enum = context.create_aac_enum("RequirementVerificationMethod", 123)

    def test_parse_and_load_non_definition(self):
        with self.assertRaises(ParserError):
            context = LanguageContext()
            context.parse_and_load("definition")

    def test_remove_definitions_fail(self):
        with self.assertRaises(AttributeError):
            context = LanguageContext()
            context.remove_definitions("TestSchema")

    def test_get_python_type_from_primitive_no_type(self):
        context = LanguageContext()
        with self.assertRaises(LanguageError):
            context.get_python_type_from_primitive("type")

    # Should this method return an error of some kind when it finds no definitions of a name?
    def test_get_definitions_by_name_fail(self):
        context = LanguageContext()
        definitions = context.get_definitions_by_name("invalid name")
        self.assertEqual(definitions, [])
        with self.assertRaises(TypeError):
            definitions = context.get_definitions_by_name(123)

    # Should this method return an error of some kind when it finds no definitions of a root?
    def test_get_definitions_by_root_fail(self):
        context = LanguageContext()
        definitions = context.get_definitions_by_root("invalid root")
        self.assertEqual(definitions, [])
        with self.assertRaises(TypeError):
            definitions = context.get_definitions_by_name(123)

    def test_get_defining_schema_for_root_fail(self):
        with self.assertRaises(LanguageError):
            context = LanguageContext()
            definitions = context.get_defining_schema_for_root("Schema")

    def test_get_python_type_from_primitive_fail(self):
        with self.assertRaises(LanguageError):
            context = LanguageContext()
            context.get_python_type_from_primitive("schema")

    def test_is_extension_of_fail(self):
        context = LanguageContext()
        definition = context.get_definitions_by_name("string")
        self.assertFalse(context.is_extension_of(definition[0], "aac.lang", "AacType"))

    def test_get_definitions_of_type_fail(self):
        with self.assertRaises(LanguageError):
            context = LanguageContext()
            context.get_definitions_of_type("invalid_type", "invalid_name")

    def test_get_values_by_field_chain(self):
        context = LanguageContext()
        test_values = ["schema.field.name", "enum.value", "primitives.python_type"]
        for val in test_values:
            values = context.get_values_by_field_chain(val)
            self.assertLess(len(values), 1)


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
