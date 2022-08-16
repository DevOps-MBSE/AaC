import os
from unittest import TestCase

from aac.plugins.gen_design_doc.gen_design_doc_impl import gen_design_doc

from tests.helpers.assertion import assert_plugin_success
from tests.helpers.io import temporary_test_file


class TestGenerateDesignDocumentPlugin(TestCase):
    def test_can_generate_design_doc_with_models(self):
        with temporary_test_file(TEST_MODEL) as test_model: 
            temp_dir = os.path.dirname(test_model.name)
            result = gen_design_doc(test_model.name, temp_dir)
            assert_plugin_success(result) 
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 2)
            test_design_doc_file_name, *_ = [
                f for f in files if f != os.path.basename(test_model.name)
            ]
            with open(os.path.join(temp_dir, test_design_doc_file_name)) as markdown_file:
                document_title = os.path.basename(test_model.name)
                markdown = markdown_file.read()
                self.assert_headings(markdown, document_title)
                self.assert_schema(markdown)
                self.assert_model(markdown)
                self.assert_use_case(markdown)
   
    def test_can_handle_names_with_dots(self):
        with temporary_test_file(TEST_MODEL_2) as test_yaml:
            result = gen_design_doc(test_yaml.name, os.path.dirname(test_yaml.name))
            assert_plugin_success(result)
            
            temp_dir = os.path.dirname(test_yaml.name)
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 2)
    
            test_design_doc_file_name, *_ = [
                f for f in files if f != os.path.basename(test_yaml.name)
            ]

            with open(os.path.join(temp_dir, test_design_doc_file_name)) as markdown_file:
                self.assertIn("SubSchema.Schema1 data", markdown_file.read())

    def assert_headings(self, markdown: str, document_title: str) -> None:
        patterns = [
            document_title,
            "Schema",
            "Model",
            "Use Cases",
            "Behavior",
            "Participants",
            "Steps",
        ]

        [self.assertIn(f"# {name}", markdown) for name in patterns]

    def assert_schema(self, markdown: str) -> None:
        names = ["x", "y", "z", "i", "j", "direction"]
        required = [n for n in names if n != "direction"]
        [
            self.assertIn(f"number {n}{' (required)' if n in required else ''}", markdown)
            for n in names
        ]

    def assert_model(self, markdown: str) -> None:
        patterns = [
            "test model",
            "a system to do things",
            "pub-sub",
            "- Point alpha",
            "- Point beta",
            "- number gamma",
            "Given",
            "When",
            "Then",
        ]

        [self.assertIn(pattern, markdown) for pattern in patterns]

    def assert_use_case(self, markdown: str) -> None:
        patterns = ["move an object", "Source", "Target", "Action"]
        [self.assertIn(pattern, markdown) for pattern in patterns]

TEST_MODEL = """
schema:
  name: Vector
  fields:
    - name: i
      type: number
    - name: j
      type: number
    - name: direction
      type: number
      description: If direction is not provided, it will default to 1.
  validation:
    - name: Required fields are present
      arguments:
        - i
        - j
---
schema:
  name: Point
  fields:
    - name: x
      type: number
    - name: y
      type: number
    - name: z
      type: number
  validation:
    - name: Required fields are present
      arguments:
        - x
        - y
        - z
---
model:
  name: test model
  description: a system to do things
  behavior:
    - name: do something great
      description: have the system do something great
      type: pub-sub
      input:
        - name: alpha
          type: Point
        - name: beta
          type: Point
      output:
        - name: gamma
          type: number
        - name: delta
          type: Vector
      acceptance:
        - scenario: move from point alpha to point beta
          given:
            - Point alpha is (1, 2, 3)
            - Point beta is (2, 3, 4)
            - I am at point alpha
          when:
            - I move from point alpha to point beta
          then:
            - I am at point beta
            - publish gamma: the time it took me to finish
            - publish delta: some vector
        - scenario: move from point beta back to point alpha
          given:
            - Point alpha is (1, 2, 3)
            - Point beta is (2, 3, 4)
            - I am at point beta
          when:
            - I move from point beta to point alpha
          then:
            - I am at point alpha
            - publish gamma: the time it took me to finsh
            - publish delta: some vector
---
usecase:
  name: move an item
  description: the user wants to move an object from one place to another
  participants:
    - name: model1
      type: test model
    - name: model2
      type: test model
  steps:
    - step: move an object from one place to another
      source: model1
      target: model2
      action: move from point alpha to point beta
    - step: move an object back to it's original location
      source: model2
      target: model1
      action: move from point beta back to point alpha
"""
TEST_MODEL_2 = """
schema:
  name: Schema1
  fields:
    - name: data
      type: SubSchema.Schema1
---
schema:
  name: SubSchema.Schema1
  fields:
    - name: data
      type: string
"""
