import os
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import TestCase

from aac_gen_gherkin_behaviors.aac_gen_gherkin_behaviors_impl import gen_gherkin_behaviors


class TestGenerateGherkinBehaviorsPlugin(TestCase):
    def test_gen_gherkin_behaviors_with_one_behavior_multiple_scenarios(self):
        behavior_name_1 = "First Behavior"
        behavior_description_1 = "Takes inspiration from the universe and creates magical beans"

        # Scenario 1
        behavior_scenario_1 = "convert inspiration to magical beans"
        behavior_scenario_1_given_1 = "a feeling of hope from the universe"
        behavior_scenario_1_when_1 = (
            "the feeling of hope is empowering and it instills inspiration"
        )
        behavior_scenario_1_then_1 = "the energy of inspiration manifests as magical beans"

        # Scenario 1
        behavior_scenario_2 = "convert inspiration to magical beans"
        behavior_scenario_2_given_1 = "a feeling of wonder from the universe"
        behavior_scenario_2_given_2 = "a feeling of awe from the universe"
        behavior_scenario_2_when_1 = (
            "the feelings of wonder and awe are empowering and they instill inspiration"
        )
        behavior_scenario_2_then_1 = "the energy of inspiration manifests as magical beans"

        VALID_MODEL_WITH_SEVERAL_BEHAVIORS = f"""
---
model:
    name: test-model
    description: test model
    behavior:
        - name: {behavior_name_1}
          type: command
          description: {behavior_description_1}
          acceptance:
            - scenario: {behavior_scenario_1}
              given:
                - {behavior_scenario_1_given_1}
              when:
                - {behavior_scenario_1_when_1}
              then:
                - {behavior_scenario_1_then_1}
            - scenario: {behavior_scenario_2}
              given:
                - {behavior_scenario_2_given_1}
                - {behavior_scenario_2_given_2}
              when:
                - {behavior_scenario_2_when_1}
              then:
                - {behavior_scenario_2_then_1}
"""

        with TemporaryDirectory() as temp_output_dir:
            temp_arch_file = NamedTemporaryFile(mode="w")
            temp_arch_file.write(VALID_MODEL_WITH_SEVERAL_BEHAVIORS)
            temp_arch_file.seek(0)

            # Generate gherkin files to temp directory
            gen_gherkin_behaviors(temp_arch_file.name, temp_output_dir)

            # Check the generated files
            self.assertEqual(1, len(os.listdir(temp_output_dir)))

            temp_output_file_path = os.path.join(temp_output_dir, os.listdir(temp_output_dir)[0])
            with open(temp_output_file_path, "r") as temp_gherkin_feature_file:
                gherkin_feature_file_content = temp_gherkin_feature_file.read()

                self.assertIn(f"Feature: {behavior_description_1}", gherkin_feature_file_content)

                self.assertIn(f"Scenario: {behavior_scenario_1}", gherkin_feature_file_content)
                self.assertIn(f"Given {behavior_scenario_1_given_1}", gherkin_feature_file_content)
                self.assertIn(f"When {behavior_scenario_1_when_1}", gherkin_feature_file_content)
                self.assertIn(f"Then {behavior_scenario_1_then_1}", gherkin_feature_file_content)

                self.assertIn(f"Scenario: {behavior_scenario_2}", gherkin_feature_file_content)
                self.assertIn(f"Given {behavior_scenario_2_given_1}", gherkin_feature_file_content)
                self.assertIn(f"And {behavior_scenario_2_given_2}", gherkin_feature_file_content)
                self.assertIn(f"When {behavior_scenario_2_when_1}", gherkin_feature_file_content)
                self.assertIn(f"Then {behavior_scenario_2_then_1}", gherkin_feature_file_content)

    def test_gen_gherkin_behaviors_with_gherkin_keyword_collisions(self):
        behavior_name_1 = "First Behavior"
        behavior_description_1 = "Takes inspiration from the universe and create magical beans"

        # Scenario 1
        behavior_scenario_1 = "convert inspiration to magical beans"
        behavior_scenario_1_given_1 = "Given a feeling of wonder from the universe"
        behavior_scenario_1_given_2 = "Given a feeling of awe from the universe"
        behavior_scenario_1_when_1 = "Then the feelings of wonder and awe are empowering"
        behavior_scenario_1_when_2 = "Then the feelings empowerment instills inspiration"
        behavior_scenario_1_then_1 = (
            "When the energy of inspiration manifests as a magical beanstalk"
        )
        behavior_scenario_1_then_2 = "When the magical beanstalk grows magical bean pods"

        VALID_MODEL_WITH_SEVERAL_BEHAVIORS = f"""
---
model:
    name: test-model
    description: test model
    behavior:
        - name: {behavior_name_1}
          type: command
          description: {behavior_description_1}
          acceptance:
            - scenario: {behavior_scenario_1}
              given:
                - {behavior_scenario_1_given_1}
                - {behavior_scenario_1_given_2}
              when:
                - {behavior_scenario_1_when_1}
                - {behavior_scenario_1_when_2}
              then:
                - {behavior_scenario_1_then_1}
                - {behavior_scenario_1_then_2}
"""

        with TemporaryDirectory() as temp_output_dir:
            temp_arch_file = NamedTemporaryFile(mode="w")
            temp_arch_file.write(VALID_MODEL_WITH_SEVERAL_BEHAVIORS)
            temp_arch_file.seek(0)

            # Generate gherkin files to temp directory
            gen_gherkin_behaviors(temp_arch_file.name, temp_output_dir)

            # Check the generated files
            self.assertEqual(1, len(os.listdir(temp_output_dir)))

            temp_output_file_path = os.path.join(temp_output_dir, os.listdir(temp_output_dir)[0])
            with open(temp_output_file_path, "r") as temp_gherkin_feature_file:
                gherkin_feature_file_content = temp_gherkin_feature_file.read()

                self.assertIn(f"Feature: {behavior_description_1}", gherkin_feature_file_content)

                self.assertIn(f"Scenario: {behavior_scenario_1}", gherkin_feature_file_content)
                self.assertIn(
                    f"Given {_remove_first_word_in_string(behavior_scenario_1_given_1)}",
                    gherkin_feature_file_content,
                )
                self.assertIn(
                    f"And {_remove_first_word_in_string(behavior_scenario_1_given_2)}",
                    gherkin_feature_file_content,
                )
                self.assertIn(
                    f"When {_remove_first_word_in_string(behavior_scenario_1_when_1)}",
                    gherkin_feature_file_content,
                )
                self.assertIn(
                    f"And {_remove_first_word_in_string(behavior_scenario_1_when_2)}",
                    gherkin_feature_file_content,
                )
                self.assertIn(
                    f"Then {_remove_first_word_in_string(behavior_scenario_1_then_1)}",
                    gherkin_feature_file_content,
                )
                self.assertIn(
                    f"And {_remove_first_word_in_string(behavior_scenario_1_then_2)}",
                    gherkin_feature_file_content,
                )


def _remove_first_word_in_string(string: str) -> str:
    return string.split(None, 1)[1]
