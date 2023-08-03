import inspect
import os
from tempfile import TemporaryDirectory
from typing import Callable

from aac.io.constants import YAML_DOCUMENT_EXTENSION
from aac.lang.constants import BEHAVIOR_TYPE_REQUEST_RESPONSE
from aac.plugins.first_party.gen_plant_uml.gen_plant_uml_impl import (
    COMPONENT_STRING,
    OBJECT_STRING,
    SEQUENCE_STRING,
    PLANT_UML_FILE_EXTENSION,
    FILE_NAME_CHARACTERS_TO_REPLACE,
    puml_component,
    puml_object,
    puml_sequence,
    _get_generated_file_name,
    _get_formatted_definition_name,
)

from tests.active_context_test_case import ActiveContextTestCase
from tests.helpers.assertion import assert_plugin_success
from tests.helpers.io import TemporaryTestFile, TemporaryAaCTestFile
from tests.helpers.plugins import check_generated_file_contents


class TestGenPlantUml(ActiveContextTestCase):
    def test_formatted_definition_name(self):
        self.assertEqual(_get_formatted_definition_name(""), "")
        self.assertEqual(_get_formatted_definition_name("name"), "name")
        self.assertEqual(_get_formatted_definition_name("Name"), "name")
        self.assertEqual(_get_formatted_definition_name("Definition Name"), "definition_name")
        self.assertEqual(
            _get_formatted_definition_name(f"{FILE_NAME_CHARACTERS_TO_REPLACE}This is my Definition Name"),
            "this_is_my_definition_name",
        )
        self.assertEqual(
            _get_formatted_definition_name(f"This is my{FILE_NAME_CHARACTERS_TO_REPLACE} Definition Name"),
            "this_is_my_definition_name",
        )
        self.assertEqual(
            _get_formatted_definition_name(f"This is my Definition Name{FILE_NAME_CHARACTERS_TO_REPLACE}"),
            "this_is_my_definition_name",
        )

    def test_generated_file_name(self):
        new_output_dir = "/dir/some/tmp/"
        new_relative_dir = "tmp/"
        file_name = "test_arch_file"
        definition_name = "My test definition name."
        formatted_definition_name = _get_formatted_definition_name(definition_name)

        puml_types = [COMPONENT_STRING, OBJECT_STRING, SEQUENCE_STRING]
        filename = _convert_aac_filepath_to_filename(file_name)
        for puml_type in puml_types:
            self.assertEqual(
                _get_generated_file_name(filename, puml_type, definition_name, new_output_dir),
                os.path.join(new_output_dir, puml_type, f"{file_name}_{formatted_definition_name}{PLANT_UML_FILE_EXTENSION}"),
            )
            self.assertEqual(
                _get_generated_file_name(filename, puml_type, definition_name, new_relative_dir),
                os.path.join(
                    new_relative_dir, puml_type, f"{file_name}_{formatted_definition_name}{PLANT_UML_FILE_EXTENSION}"
                ),
            )

    def test_puml_component_diagram_to_file(self):
        with (
            TemporaryDirectory() as temp_directory,
            TemporaryTestFile(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=YAML_DOCUMENT_EXTENSION) as plugin_yaml,
        ):
            result = puml_component(plugin_yaml.name, temp_directory)

            full_output_dir = os.path.join(temp_directory, COMPONENT_STRING)
            self.assertIn(full_output_dir, result.get_messages_as_string())
            assert_plugin_success(result)

            filename = _convert_aac_filepath_to_filename(plugin_yaml.name)
            expected_puml_file_paths = [
                _get_generated_file_name(filename, COMPONENT_STRING, name, temp_directory)
                for name in [TEST_PUML_SYSTEM_TYPE, TEST_PUML_SERVICE_ONE_TYPE, TEST_PUML_SERVICE_TWO_TYPE]
            ]
            temp_directory_files = os.listdir(full_output_dir)
            for path in expected_puml_file_paths:
                basename = os.path.basename(path)
                self.assertIn(basename, temp_directory_files)

                parts = os.path.splitext(basename)[0].replace("-", "").split("_")
                check_generated_file_contents(path, self._get_checker_from_filepath(parts[-1], COMPONENT_STRING))

    def test_puml_object_diagram_to_file(self):
        with (
            TemporaryDirectory() as temp_directory,
            TemporaryTestFile(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=YAML_DOCUMENT_EXTENSION) as plugin_yaml,
        ):
            full_output_dir = os.path.join(temp_directory, OBJECT_STRING)

            result = puml_object(plugin_yaml.name, temp_directory)
            self.assertIn(full_output_dir, result.get_messages_as_string())
            assert_plugin_success(result)

            temp_directory_files = os.listdir(full_output_dir)

            filename = _convert_aac_filepath_to_filename(plugin_yaml.name)
            expected_puml_file_path = _get_generated_file_name(filename, OBJECT_STRING, filename, temp_directory)
            self.assertIn(os.path.basename(expected_puml_file_path), temp_directory_files)

            with open(expected_puml_file_path) as generated_puml_file:
                self._check_object_diagram_content(generated_puml_file.read())

    def test_puml_sequence_diagram_to_file(self):
        with (
            TemporaryDirectory() as temp_directory,
            TemporaryTestFile(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=YAML_DOCUMENT_EXTENSION) as plugin_yaml,
        ):
            result = puml_sequence(plugin_yaml.name, temp_directory)

            full_output_dir = os.path.join(temp_directory, SEQUENCE_STRING)
            self.assertIn(full_output_dir, result.get_messages_as_string())
            assert_plugin_success(result)

            filename = _convert_aac_filepath_to_filename(plugin_yaml.name)
            expected_puml_file_paths = [
                _get_generated_file_name(filename, SEQUENCE_STRING, name, temp_directory)
                for name in [TEST_PUML_USE_CASE_ONE_TITLE, TEST_PUML_USE_CASE_TWO_TITLE]
            ]
            temp_directory_files = os.listdir(full_output_dir)
            for path in expected_puml_file_paths:
                basename = os.path.basename(path)
                self.assertIn(basename, temp_directory_files)

                _, *parts = os.path.splitext(basename)[0].split("_")
                check_generated_file_contents(path, self._get_checker_from_filepath("_".join(parts[-2:]), SEQUENCE_STRING))

    def _get_checker_from_filepath(self, path: str, puml_type: str) -> Callable:
        """Get the method used to check the content in the generated file.

        Methods are expected to have a specific naming format:
            `_check_{puml_type}_diagram_<whatever else>`
        where <whatever else> contains the path string.

        Args:
            path (str): The portion of the filename that corresponds to the checker's name.
            puml_type (str): The type of diagram that was generated.

        Returns:
            The method on self that checks the generated content for the file from which path was
            extracted.
        """

        def is_checker(obj):
            return inspect.ismethod(obj) and obj.__name__.startswith(f"_check_{puml_type}_diagram")

        checkers = inspect.getmembers(self, is_checker)
        return [method for (name, method) in checkers if path in name].pop()

    def _check_component_diagram_testsystem(self, component_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(component_diagram_content_string)
        self._check_component_diagram_serviceone(component_diagram_content_string)
        self._check_component_diagram_servicetwo(component_diagram_content_string)
        self.assertIn(f'component "{TEST_PUML_SYSTEM_TYPE}"', component_diagram_content_string)

    def _check_component_diagram_serviceone(self, component_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(component_diagram_content_string)
        self._assert_component_diagram_relations(
            component_diagram_content_string,
            "-->",
            [
                {"left": TEST_PUML_DATA_A_TYPE, "right": f"{TEST_PUML_SERVICE_ONE_TYPE}", "name": "in"},
                {"left": f"{TEST_PUML_SERVICE_ONE_TYPE}", "right": TEST_PUML_DATA_B_TYPE, "name": "out"},
            ],
        )

    def _check_component_diagram_servicetwo(self, component_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(component_diagram_content_string)
        self._assert_component_diagram_relations(
            component_diagram_content_string,
            "-->",
            [
                {"left": TEST_PUML_DATA_B_TYPE, "right": f"{TEST_PUML_SERVICE_TWO_TYPE}", "name": "in"},
                {"left": f"{TEST_PUML_SERVICE_TWO_TYPE}", "right": TEST_PUML_DATA_C_TYPE, "name": "out"},
            ],
        )

    def _assert_component_diagram_relations(self, content: str, relation: str, links: list[dict[str, str]]):
        for link in links:
            self.assertIn(f"{link.get('left')} {relation} {link.get('right')} : {link.get('name')}", content)

    def _check_object_diagram_content(self, object_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(object_diagram_content_string)
        self._assert_object_diagram_object(
            object_diagram_content_string, [TEST_PUML_SYSTEM_TYPE, TEST_PUML_SERVICE_ONE_TYPE, TEST_PUML_SERVICE_TWO_TYPE]
        )
        self._assert_object_diagram_object_relations(
            object_diagram_content_string,
            "*--",
            [
                {"left": TEST_PUML_SYSTEM_TYPE, "right": TEST_PUML_SERVICE_ONE_TYPE},
                {"left": TEST_PUML_SYSTEM_TYPE, "right": TEST_PUML_SERVICE_TWO_TYPE},
            ],
        )

    def _assert_object_diagram_object(self, content: str, objects: list[str]):
        for obj in objects:
            self.assertIn(f"object {obj}", content)

    def _assert_object_diagram_object_relations(self, content: str, relation: str, relationships: list[dict[str, str]]):
        for relationship in relationships:
            self.assertIn(f"{relationship.get('left')} {relation} {relationship.get('right')}", content)

    def _check_sequence_diagram_usecase_one(self, sequence_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(sequence_diagram_content_string)
        self.assertIn(f"title {TEST_PUML_USE_CASE_ONE_TITLE}", sequence_diagram_content_string)
        self._assert_sequence_diagram_participants(
            sequence_diagram_content_string,
            [
                {"name": TEST_PUML_SYSTEM_NAME, "type": TEST_PUML_SYSTEM_TYPE},
                {"name": TEST_PUML_SERVICE_ONE_NAME, "type": TEST_PUML_SERVICE_ONE_TYPE},
                {"name": TEST_PUML_SERVICE_TWO_NAME, "type": TEST_PUML_SERVICE_TWO_TYPE},
            ],
        )
        self._assert_sequence_diagram_io(
            sequence_diagram_content_string,
            [
                {"in": TEST_PUML_SYSTEM_NAME, "out": TEST_PUML_SERVICE_ONE_NAME},
                {"in": TEST_PUML_SERVICE_TWO_NAME, "out": TEST_PUML_SYSTEM_NAME},
            ],
        )

    def _check_sequence_diagram_usecase_two(self, sequence_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(sequence_diagram_content_string)
        self.assertIn(f"title {TEST_PUML_USE_CASE_TWO_TITLE}", sequence_diagram_content_string)
        self._assert_sequence_diagram_participants(
            sequence_diagram_content_string,
            [
                {"name": TEST_PUML_SERVICE_ONE_NAME, "type": TEST_PUML_SERVICE_ONE_TYPE},
                {"name": TEST_PUML_SERVICE_TWO_NAME, "type": TEST_PUML_SERVICE_TWO_TYPE},
            ],
        )
        self._assert_sequence_diagram_io(
            sequence_diagram_content_string,
            [
                {"in": TEST_PUML_SERVICE_ONE_NAME, "out": TEST_PUML_SERVICE_TWO_NAME},
                {"in": TEST_PUML_SERVICE_TWO_NAME, "out": TEST_PUML_SERVICE_ONE_NAME},
            ],
        )

    def _assert_sequence_diagram_participants(self, content: str, participants: list[dict[str, str]]):
        for participant in participants:
            self.assertIn(f"participant {participant.get('type')} as {participant.get('name')}", content)

    def _assert_sequence_diagram_io(self, content: str, inputs_outputs: list[dict[str, str]]):
        for io in inputs_outputs:
            self.assertIn(f"{io.get('in')} -> {io.get('out')} : ", content)

    def _assert_diagram_contains_uml_boilerplate(self, puml_file):
        self.assertIn("@startuml", puml_file)
        self.assertIn("@enduml", puml_file)


def _convert_aac_filepath_to_filename(filepath: str) -> str:
    aac_file_name, _ = os.path.splitext(os.path.basename(filepath))
    return aac_file_name


TEST_PUML_SYSTEM_NAME = "Test-System"
TEST_PUML_SYSTEM_TYPE = "System"
TEST_PUML_SERVICE_ONE_NAME = "svc1"
TEST_PUML_SERVICE_ONE_TYPE = "ServiceOne"
TEST_PUML_SERVICE_TWO_NAME = "svc2"
TEST_PUML_SERVICE_TWO_TYPE = "ServiceTwo"
TEST_PUML_SERVICE_THREE_NAME = "svc3"
TEST_PUML_SERVICE_THREE_TYPE = "ServiceThree"
TEST_PUML_EXTERNAL_SYSTEM_NAME = "ext"
TEST_PUML_EXTERNAL_SYSTEM_TYPE = "ExternalSystem"
TEST_PUML_DATA_A_TYPE = "DataA"
TEST_PUML_DATA_B_TYPE = "DataB"
TEST_PUML_DATA_C_TYPE = "DataC"
TEST_PUML_USE_CASE_ONE_TITLE = "Nominal flow within the system usecase one."
TEST_PUML_USE_CASE_TWO_TITLE = "Request/response flow usecase two."

TEST_PUML_ARCH_YAML = f"""
model:
  name: {TEST_PUML_SYSTEM_TYPE}
  description: A simple distributed system model
  components:
    - name: {TEST_PUML_SERVICE_ONE_NAME}
      type: {TEST_PUML_SERVICE_ONE_TYPE}
    - name: {TEST_PUML_SERVICE_TWO_NAME}
      type: {TEST_PUML_SERVICE_TWO_TYPE}
  behavior:
    - name: Process {TEST_PUML_DATA_A_TYPE} Request to {TEST_PUML_DATA_C_TYPE} Response
      type: {BEHAVIOR_TYPE_REQUEST_RESPONSE}
      description: process {TEST_PUML_DATA_A_TYPE} and respond with {TEST_PUML_DATA_C_TYPE}
      input:
        - name: in
          type: {TEST_PUML_DATA_A_TYPE}
      output:
        - name: out
          type: {TEST_PUML_DATA_C_TYPE}
      acceptance:
        - scenario: Receive {TEST_PUML_DATA_A_TYPE} request and return {TEST_PUML_DATA_C_TYPE} response
          given:
            - System is running
            - {TEST_PUML_SERVICE_ONE_TYPE} is running
            - Subsystem is running
            - ServiceThree is running
          when:
            - System receives a {TEST_PUML_DATA_A_TYPE} request
          then:
            - System processes the request into a {TEST_PUML_DATA_C_TYPE} response
            - System returns the {TEST_PUML_DATA_C_TYPE} response
---
model:
  name: {TEST_PUML_SERVICE_ONE_TYPE}
  behavior:
    - name: Process {TEST_PUML_DATA_A_TYPE} Request
      type: {BEHAVIOR_TYPE_REQUEST_RESPONSE}
      description: Process a {TEST_PUML_DATA_A_TYPE} request and return a {TEST_PUML_DATA_B_TYPE} response
      input:
        - name: in
          type: {TEST_PUML_DATA_A_TYPE}
      output:
        - name: out
          type: {TEST_PUML_DATA_B_TYPE}
      acceptance:
        - scenario: Receive {TEST_PUML_DATA_A_TYPE} request and return {TEST_PUML_DATA_B_TYPE} response
          given:
            - {TEST_PUML_SERVICE_ONE_TYPE} is running
          when:
            - {TEST_PUML_SERVICE_ONE_TYPE} receives a {TEST_PUML_DATA_A_TYPE} request
          then:
            - {TEST_PUML_SERVICE_ONE_TYPE} processes the request into a {TEST_PUML_DATA_B_TYPE} response
            - {TEST_PUML_SERVICE_ONE_TYPE} returns the {TEST_PUML_DATA_B_TYPE} response
        - scenario: Receive invalid request
          given:
            - {TEST_PUML_SERVICE_ONE_TYPE} is running
          when:
            - {TEST_PUML_SERVICE_ONE_TYPE} receives request that isn't a {TEST_PUML_DATA_A_TYPE} request
          then:
            - {TEST_PUML_SERVICE_ONE_TYPE} returns an error response code
---
model:
  name: {TEST_PUML_SERVICE_TWO_TYPE}
  behavior:
    - name: Process {TEST_PUML_DATA_B_TYPE} Request
      type: {BEHAVIOR_TYPE_REQUEST_RESPONSE}
      description: Process a {TEST_PUML_DATA_B_TYPE} request and return a {TEST_PUML_DATA_C_TYPE} response
      input:
        - name: in
          type: {TEST_PUML_DATA_B_TYPE}
      output:
        - name: out
          type: {TEST_PUML_DATA_C_TYPE}
      acceptance:
        - scenario: Receive {TEST_PUML_DATA_B_TYPE} request and return {TEST_PUML_DATA_C_TYPE} response
          given:
            - {TEST_PUML_SERVICE_TWO_TYPE} is running
          when:
            - {TEST_PUML_SERVICE_TWO_TYPE} receives a {TEST_PUML_DATA_B_TYPE} request
          then:
            - {TEST_PUML_SERVICE_TWO_TYPE} processes the request into a {TEST_PUML_DATA_C_TYPE} response
            - {TEST_PUML_SERVICE_TWO_TYPE} returns the {TEST_PUML_DATA_C_TYPE} response
---
schema:
  name: {TEST_PUML_DATA_A_TYPE}
  fields:
  - name: msg
    type: string
---
schema:
  name: {TEST_PUML_DATA_B_TYPE}
  fields:
  - name: msg
    type: string
---
schema:
  name: {TEST_PUML_DATA_C_TYPE}
  fields:
  - name: msg
    type: string
---
usecase:
  name: {TEST_PUML_USE_CASE_ONE_TITLE}
  description:
  participants:
    - name: {TEST_PUML_SYSTEM_NAME}
      type: {TEST_PUML_SYSTEM_TYPE}
    - name: {TEST_PUML_SERVICE_ONE_NAME}
      type: {TEST_PUML_SERVICE_ONE_TYPE}
    - name: {TEST_PUML_SERVICE_TWO_NAME}
      type: {TEST_PUML_SERVICE_TWO_TYPE}
  steps:
    - step: The system has been invoked to doFlow which triggers {TEST_PUML_SERVICE_ONE_NAME}
      source: {TEST_PUML_SYSTEM_NAME}
      target: {TEST_PUML_SERVICE_ONE_NAME}
      action: ProcessDataA
    - step: {TEST_PUML_SERVICE_ONE_NAME} completes and calls {TEST_PUML_SERVICE_TWO_NAME} to continue the flow
      source: {TEST_PUML_SERVICE_ONE_NAME}
      target: {TEST_PUML_SERVICE_TWO_NAME}
      action: ProcessDataB
    - step: svc3 completes and provides the result back to {TEST_PUML_SYSTEM_NAME}
      source: {TEST_PUML_SERVICE_TWO_NAME}
      target: {TEST_PUML_SYSTEM_NAME}
      action: doFlow
---
usecase:
  name: {TEST_PUML_USE_CASE_TWO_TITLE}
  description: A sample independent flow.
  participants:
    - name: {TEST_PUML_SERVICE_ONE_NAME}
      type: {TEST_PUML_SERVICE_ONE_TYPE}
    - name: {TEST_PUML_SERVICE_TWO_NAME}
      type: {TEST_PUML_SERVICE_TWO_TYPE}
  steps:
    - step: {TEST_PUML_SERVICE_ONE_NAME} makes a request for data from {TEST_PUML_SERVICE_TWO_NAME}
      source: {TEST_PUML_SERVICE_ONE_NAME}
      target: {TEST_PUML_SERVICE_TWO_NAME}
      action: sendRequestToServiceTwo
    - step: {TEST_PUML_SERVICE_TWO_NAME} completes and provides the result back to {TEST_PUML_SERVICE_ONE_NAME}
      source: {TEST_PUML_SERVICE_TWO_NAME}
      target: {TEST_PUML_SERVICE_ONE_NAME}
      action: respondToServiceOne
"""
