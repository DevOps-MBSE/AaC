from unittest import TestCase

from aac import parser
from aac.genplug import (
    GeneratePluginException,
    _compile_templates,
    _convert_template_name_to_file_name,
)
from aac.validator import validation

INIT_TEMPLATE_NAME = "__init__.py.jinja2"
PLUGIN_TEMPLATE_NAME = "plugin.py.jinja2"
PLUGIN_IMPL_TEMPLATE_NAME = "plugin_impl.py.jinja2"
PLUGIN_IMPL_TEST_TEMPLATE_NAME = "test_plugin_impl.py.jinja2"
SETUP_TEMPLATE_NAME = "setup.py.jinja2"
README_TEMPLATE_NAME = "README.md.jinja2"


class TestGenPlug(TestCase):
    def test_convert_template_name_to_file_name(self):
        plugin_name = "aac-test"
        template_names = [
            INIT_TEMPLATE_NAME,
            PLUGIN_TEMPLATE_NAME,
            PLUGIN_IMPL_TEMPLATE_NAME,
            SETUP_TEMPLATE_NAME,
        ]
        expected_filenames = [
            "__init__.py",
            f"{plugin_name}.py",
            f"{plugin_name}_impl.py",
            "setup.py",
        ]

        for i in range(len(template_names)):
            expected_filename = expected_filenames[i]
            actual_filename = _convert_template_name_to_file_name(template_names[i], plugin_name)
            self.assertEqual(expected_filename, actual_filename)

    def test_compile_templates(self):
        with validation(
            parser.parse_str, "", model_content=TEST_PLUGIN_YAML_STRING
        ) as parsed_model:
            plugin_name = "aac_gen_protobuf"

            generated_templates = _compile_templates(parsed_model)

            generated_template_names = []
            generated_template_parent_directories = []
            for template in generated_templates.values():
                generated_template_names.append(template.file_name)
                generated_template_parent_directories.append(template.parent_dir)

            # Check that the files don't have "-" in the name
            for name in generated_template_names:
                self.assertNotIn("-", name)

            # Check that the expected files and directories were created and named correctly
            num_generated_templates = len(generated_templates)
            self.assertEqual(len(generated_template_names), num_generated_templates)
            self.assertEqual(len(generated_template_parent_directories), num_generated_templates)

            # Assert that the expected template files were generated
            self.assertIn("__init__.py", generated_template_names)
            self.assertIn("setup.py", generated_template_names)
            self.assertIn("README.md", generated_template_names)
            self.assertIn(f"{plugin_name}.py", generated_template_names)
            self.assertIn(f"{plugin_name}_impl.py", generated_template_names)
            self.assertIn(f"test_{plugin_name}_impl.py", generated_template_names)

            self.assertIn("tests", generated_template_parent_directories)

            # Assert that some expected content is present
            generated_plugin_file_contents = generated_templates.get(PLUGIN_TEMPLATE_NAME).content
            self.assertIn("@aac.hookimpl", generated_plugin_file_contents)
            self.assertIn("gen_protobuf_arguments", generated_plugin_file_contents)
            self.assertIn("import gen_protobuf", generated_plugin_file_contents)
            self.assertIn("architecture_file", generated_plugin_file_contents)
            self.assertIn("output_directory", generated_plugin_file_contents)

            # Assert Model Extensions were generated
            self.assertIn("get_base_model_extensions", generated_plugin_file_contents)
            self.assertIn("PLUGIN_EXTENSION_YAML", generated_plugin_file_contents)
            self.assertIn("name: ProtobufDataType", generated_plugin_file_contents)
            self.assertIn("name: ProtobufTypeField", generated_plugin_file_contents)

            generated_plugin_impl_file_contents = generated_templates.get(
                PLUGIN_IMPL_TEMPLATE_NAME
            ).content
            self.assertIn("def gen_protobuf", generated_plugin_impl_file_contents)
            self.assertIn("architecture_file: str", generated_plugin_impl_file_contents)
            self.assertIn("output_directory: string", generated_plugin_impl_file_contents)
            self.assertIn("raise NotImplementedError", generated_plugin_impl_file_contents)

            generated_plugin_impl_test_file_contents = generated_templates.get(
                PLUGIN_IMPL_TEST_TEMPLATE_NAME
            ).content
            self.assertIn("TestAacGenProtobuf(TestCase)", generated_plugin_impl_test_file_contents)
            self.assertIn("TODO: Write tests", generated_plugin_impl_test_file_contents)
            self.assertIn("self.assertTrue(False)", generated_plugin_impl_test_file_contents)

            generated_plugin_impl_test_file_parent_dir = generated_templates.get(
                PLUGIN_IMPL_TEST_TEMPLATE_NAME
            ).parent_dir
            self.assertEqual(generated_plugin_impl_test_file_parent_dir, "tests")

            generated_readme_file_contents = generated_templates.get(README_TEMPLATE_NAME).content
            self.assertIn("# aac-gen-protobuf", generated_readme_file_contents)
            self.assertIn("## Command:", generated_readme_file_contents)
            self.assertIn("## Plugin Extensions and Definitions", generated_readme_file_contents)
            self.assertIn("$ aac gen-protobuf", generated_readme_file_contents)
            self.assertIn("### Ext", generated_readme_file_contents)
            self.assertIn("### Enum", generated_readme_file_contents)

    def test__compile_templates_errors_on_multiple_models(self):
        with validation(
            parser.parse_str,
            "",
            model_content=f"{TEST_PLUGIN_YAML_STRING}\n---\n{SECONDARY_MODEL_YAML_DEFINITION}",
        ) as parsed_model:
            self.assertRaises(GeneratePluginException, _compile_templates, parsed_model)

    def test__compile_templates_with_model_name_missing_package_prefix(self):
        parsed_model = parser.parse_str("", MODEL_YAML_DEFINITION_SANS_PACKAGE_PREFIX)
        plugin_name = "aac_spec"

        generated_templates = _compile_templates(parsed_model)

        generated_template_names = []
        generated_template_parent_directories = []
        for template in generated_templates.values():
            generated_template_names.append(template.file_name)
            generated_template_parent_directories.append(template.parent_dir)

        # Check that the files don't have "-" in the name
        for name in generated_template_names:
            self.assertNotIn("-", name)

        # Check that the expected files and directories were created and named correctly
        num_generated_templates = len(generated_templates)
        self.assertEqual(len(generated_template_names), num_generated_templates)
        self.assertEqual(len(generated_template_parent_directories), num_generated_templates)

        self.assertIn("__init__.py", generated_template_names)
        self.assertIn("setup.py", generated_template_names)
        self.assertIn("README.md", generated_template_names)
        self.assertIn(f"{plugin_name}.py", generated_template_names)
        self.assertIn(f"{plugin_name}_impl.py", generated_template_names)
        self.assertIn(f"test_{plugin_name}_impl.py", generated_template_names)

        self.assertIn("tests", generated_template_parent_directories)


TEST_PLUGIN_YAML_STRING = """
model:
  name: aac-gen-protobuf
  description: aac-gen-protobuf is an Architecture-as-Code plugin that generates protobuf message definitions from Architecture-as-Code models.
  behavior:
    - name: gen-protobuf
      type: command
      description: Generate protobuf messages from Arch-as-Code models
      input:
        - name: architecture_file
          type: string
          python_type: str
          description: The yaml file containing the data models to generate as Protobuf messages.
        - name: output_directory
          type: string
          description: The directory to write the generated Protobuf messages to.
      acceptance:
        - scenario: Output protobuf messages for behavior input/output entries in an Architecture model.
          given:
            - The {{gen-protobuf.input.architecture_file}} contains a valid architecture.
          when:
            - The aac app is run with the gen-protobuf command and a valid architecture file.
          then:
            - Protobuf messages are written to {{gen-protobuf.input.output_directory}}.
---
enum:
  name: ProtobufDataType
  values:
    - double
    - float
    - int32
    - int64
    - uint32
    - uint64
    - sint32
    - sint64
    - fixed32
    - fixed64
    - bool
    - string
    - bytes
---
ext:
   name: ProtobufTypeField
   type: Field
   dataExt:
      add:
        - name: protobuf_type
          type: ProtobufDataType
"""

SECONDARY_MODEL_YAML_DEFINITION = """
model:
  name: aac-spec-secondary
  description: aac-spec-secondary is a Architecture-as-Code plugin that enables requirement definition and trace in Arch-as-Code models.
  behavior:
    - name: spec-validate-2
      type: command
      description: 'Validates spec traces within the AaC model'
      input:
        - name: archFile
          type: file
        - name: parsed_model
          type: map
      acceptance:
        - scenario: Valid spec traces are modeled.
          given:
            - The {{spec-validate.input.archFile}} contains a valid architecture specification.
            - The {{spec-validate.input.parsed_model}} contains the parsed content from archFile.
          when:
            - The aac app is run with the spec-validate command.
          then:
            - A message saying spec validation was successful is printed to the console.
    - name: non-cmd-behavior-2
      type: startup
      description: You shouldn't see me
      acceptance:
        - scenario: Pretend to do something on startup.
          when:
          - when
          then:
          - then
"""

MODEL_YAML_DEFINITION_SANS_PACKAGE_PREFIX = """
model:
  name: spec
  description: An Architecture-as-Code plugin that enables requirement definition and trace in Arch-as-Code models.
  behavior:
    - name: spec-validate
      type: command
      description: 'Validates spec traces within the AaC model'
      input:
        - name: archFile
          type: file
        - name: parsed_model
          type: map
      acceptance:
        - scenario: Valid spec traces are modeled.
          given:
            - The {{spec-validate.input.archFile}} contains a valid architecture specification.
            - The {{spec-validate.input.parsed_model}} contains the parsed content from archFile.
          when:
            - The aac app is run with the spec-validate command.
          then:
            - A message saying spec validation was successful is printed to the console.
    - name: non-cmd-behavior-2
      type: startup
      description: You shouldn't see me
      acceptance:
        - scenario: Pretend to do something on startup.
          when:
          - when
          then:
          - then
"""
