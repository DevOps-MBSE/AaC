import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from aac_gen_design_doc.aac_gen_design_doc_impl import gen_design_doc


class TestGenerateDesignDocumentPlugin(TestCase):
    def test_can_generate_design_doc_with_models(self):
        with TemporaryDirectory() as temp_dir:
            test_model_file_name = f"{temp_dir}/test_model.yaml"
            test_design_doc_file_name = None
            with open(test_model_file_name, "w") as arch_file:
                arch_file.write(TEST_MODEL)

            gen_design_doc(test_model_file_name, temp_dir)

            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 2)

            test_design_doc_file_name, *_ = [
                f for f in files if f != os.path.basename(test_model_file_name)
            ]
            with open(f"{temp_dir}/{test_design_doc_file_name}", "r") as design_doc:
                markdown = design_doc.read()
                self.assert_headings(markdown)
                self.assert_data(markdown)
                self.assert_model(markdown)
                self.assert_use_case(markdown)

    def assert_headings(self, markdown: str) -> None:
        patterns = [
            "test_model",
            "Data",
            "Model",
            "Use Cases",
            "Behavior",
            "Participants",
            "Steps",
        ]

        [self.assertIn(f"# {name}", markdown) for name in patterns]

    def assert_data(self, markdown: str) -> None:
        names = ["x", "y", "z"]
        required = [n for n in names if n != "z"]
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
data:
  name: Point
  fields:
    - name: x
      type: number
    - name: y
      type: number
    - name: z
      type: number
  required:
    - x
    - y
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
      acceptance:
        - scenario: move from point alpha to point beta
          given:
            - Point alpha is (1, 2)
            - Point beta is (2, 3)
            - I am at point alpha
          when:
            - I move from point alpha to point beta
          then:
            - I am at point beta
            - publish gamma: the time it took me to finish
        - scenario: move from point beta back to point alpha
          given:
            - Point alpha is (1, 2)
            - Point beta is (2, 3)
            - I am at point beta
          when:
            - I move from point beta to point alpha
          then:
            - I am at point alpha
            - publish gamma: the time it took me to finsh
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
