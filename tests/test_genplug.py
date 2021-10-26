from unittest import TestCase

from aac import util, validator
from aac.genplug import _convert_template_name_to_file_name, compile_templates
from aac.parser import parse_str


class TestGenPlug(TestCase):
    def setUp(self):
        util.AAC_MODEL = {}
        validator.DEFINED_TYPES = []

    def test_convert_template_name_to_file_name(self):
        plugin_name = "aac-test"
        template_names = ["__init__.py.jinja2", "plugin.py.jinja2", "plugin_impl.py.jinja2"]
        expected_filenames = ["__init__.py", f"{plugin_name}.py", f"{plugin_name}_impl.py"]

        for i in range(len(template_names)):
            expected_filename = expected_filenames[i]
            actual_filename = _convert_template_name_to_file_name(template_names[i], plugin_name)
            self.assertEqual(expected_filename, actual_filename)

    def test_compile_templates(self):
        parsed_model = parse_str(TEST_PLUGIN_YAML_STRING, "")
        plugin_name = "aac_spec"

        generated_templates = compile_templates(parsed_model)

        generated_template_names = []
        for generated_template in generated_templates:
            generated_template_names.append(generated_template.file_name)

        # Check that the files don't have "-" in the name
        for name in generated_template_names:
            self.assertNotIn("-", name)

        # Check that the expected files were created and named correctly
        self.assertEqual(len(generated_template_names), 4)

        self.assertIn("__init__.py", generated_template_names)
        self.assertIn("setup.py", generated_template_names)
        self.assertIn(f"{plugin_name}.py", generated_template_names)
        self.assertIn(f"{plugin_name}_impl.py", generated_template_names)


TEST_PLUGIN_YAML_STRING = """
data:
  name: Specification
  fields:
    - name: name
      type: string
    - name: description
      type: string
    - name: subspecs
      type: string[]
    - name: sections
      type: SpecSection[]
    - name: requirements
      type: Requirement[]
  required:
    - name
---
data:
  name: SpecSection
  fields:
    - name: name
      type: string
    - name: description
      type: string
    - name: requirements
      type: Requirement[]
  required:
    - name
---
data:
  name: Requirement
  fields:
    - name: id
      type: string
    - name: shall
      type: string
    - name: parent
      type: string
    - name: attributes
      type: RequirementAttribute[]
  required:
    - id
    - shall
---
data:
  name: RequirementAttribute
  fields:
    - name: name
      type: string
    - name: value
      type: string
  required:
    - name
    - value
---
ext:
  name: addSpecificationToRoot
  type: root
  dataExt:
    add:
      - name: spec
        type: Specification
---
ext:
   name: CommandBehaviorType
   type: BehaviorType
   enumExt:
      add:
         - command
---
model:
  name: aac-spec
  description: aac-spec is a Architecture-as-Code plugin that enables requirement definition and trace in Arch-as-Code models.
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
    - name: non-cmd-behavior
      type: startup
      description: You shouldn't see me
      acceptance:
        - scenario: Pretend to do something on startup.
          when:
          - when
          then:
          - then

"""
