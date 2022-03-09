import os
from importlib import resources
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import TestCase

from aac import definition_helpers, parser
from aac.plugins.plugin_execution import PluginExecutionStatusCode
from aac.plugins.gen_gherkin_behaviors import (
    get_commands,
    get_plugin_aac_definitionss,
    __name__ as gen_gherkin_behaviors_module_name,
)
from aac.plugins.gen_gherkin_behaviors.gen_gherkin_behaviors_impl import (
    _create_gherkin_feature_file_name,
    gen_gherkin_behaviors,
)
from nose2.tools import params


class TestGenerateGherkinBehaviorsPlugin(TestCase):
    def test_gen_gherkin_get_commands_conforms_with_plugin_model(self):
        with resources.open_text(
            gen_gherkin_behaviors_module_name, "gen_gherkin_behaviors.yaml"
        ) as plugin_model_file:
            plugin_name = "aac-gen-gherkin-behaviors"
            plugin_model = parser.parse_str(plugin_model_file.name, plugin_model_file.read())
            commands_yaml = list(map(_filter_command_behaviors, definition_helpers.search(plugin_model.get(plugin_name), ["model", "behavior"])))

            # Assert that the commands returned by the plugin matches those defined in the yaml file
            commands_yaml_dict = {}
            for command_yaml in commands_yaml:
                commands_yaml_dict[command_yaml.get("name")] = command_yaml

            for command in get_commands():
                self.assertIn(command.name, commands_yaml_dict)
                command_yaml = commands_yaml_dict.get(command.name)

                # Assert help messages match
                self.assertEqual(command.description, definition_helpers.search(command_yaml, ["description"])[0])

                for argument in command.arguments:
                    yaml_arguments = command_yaml.get("input")
                    arg_names = [definition_helpers.search(arg, ["name"])[0] for arg in yaml_arguments]
                    # Assert argument is defined
                    self.assertIn(argument.name, arg_names)

    def test_get_plugin_aac_definitionss_conforms_with_plugin_model(self):
        with resources.open_text(
            gen_gherkin_behaviors_module_name, "gen_gherkin_behaviors.yaml"
        ) as plugin_model_file:
            plugin_model_content = plugin_model_file.read()

            self.assertEqual(plugin_model_content, get_plugin_aac_definitionss())

    def test_gen_gherkin_behaviors_with_one_behavior_multiple_scenarios(self):
        expected_filename = "First_Behavior.feature"
        behavior_name_1 = "First Behavior"
        behavior_description_1 = "Takes inspiration from the universe and creates magical beans"

        # Scenario 1
        behavior_scenario_1 = "convert inspiration to magical beans"
        behavior_scenario_1_given_1 = "a feeling of hope from the universe"
        behavior_scenario_1_when_1 = (
            "the feeling of hope is empowering and it instills inspiration"
        )
        behavior_scenario_1_then_1 = "the energy of inspiration manifests as magical beans"

        # Scenario 2
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
            result = gen_gherkin_behaviors(temp_arch_file.name, temp_output_dir)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            # Check the generated files
            self.assertEqual(1, len(os.listdir(temp_output_dir)))
            self.assertEqual(expected_filename, os.listdir(temp_output_dir)[0])

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
        expected_filename = "magic_manifests.feature"
        behavior_name_1 = "magic manifests"
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
            result = gen_gherkin_behaviors(temp_arch_file.name, temp_output_dir)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            # Check the generated files
            self.assertEqual(1, len(os.listdir(temp_output_dir)))
            self.assertEqual(expected_filename, os.listdir(temp_output_dir)[0])

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

    @params(
        ("DataA", "DataA.feature"),
        ("Data B", "Data_B.feature"),
        ("data a", "data_a.feature"),
        ("data-a", "data_a.feature"),
    )
    def test__generate_gherkin_feature_file_name(self, input_name, expected_filename):
        self.assertEqual(expected_filename, _create_gherkin_feature_file_name(input_name))


def _remove_first_word_in_string(string: str) -> str:
    return string.split(None, 1)[1]


def _filter_command_behaviors(behavior_definition: dict):
    return behavior_definition if behavior_definition.get("type") == "command" else None
