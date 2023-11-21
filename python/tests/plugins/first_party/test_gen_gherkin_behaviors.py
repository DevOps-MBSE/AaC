import os
import unittest

from importlib import resources
from nose2.tools import params
from tempfile import TemporaryDirectory

from aac.io import parser
from aac.io.constants import YAML_DOCUMENT_SEPARATOR
from aac.lang.active_context_lifecycle_manager import get_active_context
from aac.lang.constants import (
    BEHAVIOR_TYPE_REQUEST_RESPONSE,
    DEFINITION_FIELD_COMMANDS,
    DEFINITION_FIELD_HELP_TEXT,
    DEFINITION_FIELD_INPUT,
    DEFINITION_FIELD_NAME,
    ROOT_KEY_PLUGIN,
)
from aac.lang.definitions.collections import get_definition_by_name, get_definitions_as_yaml
from aac.lang.definitions.search import search, search_definition
from aac.plugins.first_party.gen_gherkin_behaviors import (
    __name__ as gen_gherkin_behaviors_module_name,
    _get_plugin_commands,
    _get_plugin_definitions,
)
from aac.plugins.first_party.gen_gherkin_behaviors.gen_gherkin_behaviors_impl import (
    _create_gherkin_feature_file_name,
    gen_gherkin_behaviors,
)

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_plugin_success
from tests.helpers.io import TemporaryAaCTestFile
from tests.helpers.parsed_definitions import (
    create_behavior_entry,
    create_requirement_entry,
    create_scenario_entry,
    create_spec_definition,
    create_spec_section_entry,
    create_model_definition,
)


class TestGenerateGherkinBehaviorsPlugin(ActiveContextTestCase):
    def test_gen_gherkin_get_commands_conforms_with_plugin_model(self):
        with resources.open_text(gen_gherkin_behaviors_module_name, "gen_gherkin_behaviors.yaml") as plugin_model_file:
            plugin_name = "Generate Gherkin Feature Files"
            plugin_parsed_definitions = parser.parse(plugin_model_file.name)

            commands_yaml = search_definition(
                get_definition_by_name(plugin_name, plugin_parsed_definitions),
                [ROOT_KEY_PLUGIN, DEFINITION_FIELD_COMMANDS],
            )

            # Assert that the commands returned by the plugin matches those defined in the yaml file
            commands_yaml_dict = {}
            for command_yaml in commands_yaml:
                commands_yaml_dict[command_yaml.get(DEFINITION_FIELD_NAME)] = command_yaml

            for command in _get_plugin_commands():
                self.assertIn(command.name, commands_yaml_dict)
                command_yaml = commands_yaml_dict.get(command.name)

                # Assert help messages match
                self.assertEqual(command.description, search(command_yaml, [DEFINITION_FIELD_HELP_TEXT])[0])

                for argument in command.arguments:
                    yaml_arguments = command_yaml.get(DEFINITION_FIELD_INPUT)
                    arg_names = [search(arg, [DEFINITION_FIELD_NAME])[0] for arg in yaml_arguments]
                    # Assert argument is defined
                    self.assertIn(argument.name, arg_names)

    def test_get_plugin_aac_definitions_conforms_with_plugin_model(self):
        with resources.open_text(gen_gherkin_behaviors_module_name, "gen_gherkin_behaviors.yaml") as plugin_model_file:
            plugin_model_content = plugin_model_file.read()

            self.assertEqual(plugin_model_content, get_definitions_as_yaml(_get_plugin_definitions()))

    def test_gen_gherkin_behaviors_with_one_behavior_multiple_scenarios(self):
        expected_filename = "First_Behavior.feature"
        behavior_name_1 = "First Behavior"
        behavior_description_1 = "Takes inspiration from the universe and creates magical beans"

        # Scenario 1
        behavior_scenario_1 = "convert inspiration to magical beans"
        behavior_scenario_1_given_1 = "a feeling of hope from the universe"
        behavior_scenario_1_when_1 = "the feeling of hope is empowering and it instills inspiration"
        behavior_scenario_1_then_1 = "the energy of inspiration manifests as magical beans"

        # Scenario 2
        behavior_scenario_2 = "convert inspiration to magical beans"
        behavior_scenario_2_given_1 = "a feeling of wonder from the universe"
        behavior_scenario_2_given_2 = "a feeling of awe from the universe"
        behavior_scenario_2_when_1 = "the feelings of wonder and awe are empowering and they instill inspiration"
        behavior_scenario_2_then_1 = "the energy of inspiration manifests as magical beans"

        VALID_MODEL_WITH_SEVERAL_BEHAVIORS = f"""
---
model:
    name: test-model
    description: test model
    behavior:
        - name: {behavior_name_1}
          type: {BEHAVIOR_TYPE_REQUEST_RESPONSE}
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

        with TemporaryDirectory() as temp_output_dir, TemporaryAaCTestFile(
            VALID_MODEL_WITH_SEVERAL_BEHAVIORS
        ) as temp_arch_file:

            # Generate gherkin files to temp directory
            result = gen_gherkin_behaviors(temp_arch_file.name, temp_output_dir)
            assert_plugin_success(result)

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
        behavior_scenario_1_then_1 = "When the energy of inspiration manifests as a magical beanstalk"
        behavior_scenario_1_then_2 = "When the magical beanstalk grows magical bean pods"

        VALID_MODEL_WITH_SEVERAL_BEHAVIORS = f"""
---
model:
  name: test-model
  description: test model
  behavior:
    - name: {behavior_name_1}
      type: {BEHAVIOR_TYPE_REQUEST_RESPONSE}
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

        with TemporaryDirectory() as temp_output_dir, TemporaryAaCTestFile(
            VALID_MODEL_WITH_SEVERAL_BEHAVIORS
        ) as temp_arch_file:

            # Generate gherkin files to temp directory
            result = gen_gherkin_behaviors(temp_arch_file.name, temp_output_dir)
            assert_plugin_success(result)

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

    @unittest.skip("Currently busted and under evaluation")
    def test_generate_gherkin_scenario_with_requirements(self):
        requirement_1_id, requirement_2_id, requirement_3_id = [f"T{i}" for i in range(1, 4)]
        requirement_1 = create_requirement_entry(requirement_1_id, "Shall do X")
        requirement_2 = create_requirement_entry(requirement_2_id, "Shall do Y")
        requirement_3 = create_requirement_entry(requirement_3_id, "Shall do Z")
        section = create_spec_section_entry("A test section", requirements=[requirement_1, requirement_2])
        spec = create_spec_definition("Test specification", requirements=[requirement_3], sections=[section])

        scenario = create_scenario_entry("Do X", when=["Something happens"], then=["X has occurred"])
        behavior = create_behavior_entry(
            "Behavior",
            description="A behavior",
            acceptance=[scenario],
            requirements=[requirement_1_id],
        )
        model = create_model_definition("A model", behavior=[behavior], requirements=[requirement_2_id])

        test_active_context = get_active_context(reload_context=True)
        test_active_context.add_definitions_to_context([spec, model])

        expected_filename = f"{behavior.get(DEFINITION_FIELD_NAME)}.feature"
        content = f"{spec.to_yaml()}{YAML_DOCUMENT_SEPARATOR}\n{model.to_yaml()}"

        with TemporaryAaCTestFile(content, "filename.aac", mode="w+") as test_file:
            output_dir = os.path.dirname(test_file.name)
            result = gen_gherkin_behaviors(test_file.name, output_dir)
            assert_plugin_success(result)

            self.assertIn(expected_filename, os.listdir(output_dir))
            with open(os.path.join(output_dir, expected_filename)) as out_file:
                content = out_file.read()

                self.assertIn(f"@{requirement_1_id}", content)
                self.assertIn(f"@{requirement_2_id}", content)
                self.assertNotIn(f"@{requirement_3_id}", content)


def _remove_first_word_in_string(string: str) -> str:
    return string.split(None, 1)[1]
