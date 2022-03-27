import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from aac.plugins.gen_plant_uml.gen_plant_uml_impl import (
    COMPONENT_STRING,
    OBJECT_STRING,
    SEQUENCE_STRING,
    YAML_FILE_EXTENSION,
    PLANT_UML_FILE_EXTENSION,
    INVALID_FILE_NAME_CHARACTERS,
    puml_component,
    puml_object,
    puml_sequence,
    _get_generated_file_name,
    _get_formatted_definition_name,
)
from aac.plugins.plugin_execution import PluginExecutionStatusCode
from tests.helpers.io import temporary_test_file


class TestGenPlantUml(TestCase):
    def test_formatted_definition_name(self):
        self.assertEqual(_get_formatted_definition_name(""), "")
        self.assertEqual(_get_formatted_definition_name("name"), "name")
        self.assertEqual(_get_formatted_definition_name("Name"), "name")
        self.assertEqual(_get_formatted_definition_name("Definition Name"), "definition_name")
        self.assertEqual(
            _get_formatted_definition_name(f"{INVALID_FILE_NAME_CHARACTERS}This is my Definition Name"),
            "this_is_my_definition_name"
        )
        self.assertEqual(
            _get_formatted_definition_name(f"This is my{INVALID_FILE_NAME_CHARACTERS} Definition Name"),
            "this_is_my_definition_name"
        )
        self.assertEqual(
            _get_formatted_definition_name(f"This is my Definition Name{INVALID_FILE_NAME_CHARACTERS}"),
            "this_is_my_definition_name"
        )

    def test_generated_file_name(self):
        orig_output_dir = "/tmp/some/dir/"
        new_output_dir = "/dir/some/tmp/"
        file_name = "test_arch_file"
        full_file_name = f"{orig_output_dir}{file_name}{PLANT_UML_FILE_EXTENSION}"
        definition_name = "My test definition name."
        formatted_definition_name = _get_formatted_definition_name(definition_name)

        puml_types = [COMPONENT_STRING, OBJECT_STRING, SEQUENCE_STRING]
        for puml_type in puml_types:
            self.assertEqual(
                _get_generated_file_name(full_file_name, puml_type, definition_name),
                os.path.join(orig_output_dir, puml_type, f"{file_name}_{formatted_definition_name}{PLANT_UML_FILE_EXTENSION}"),
            )
            self.assertEqual(
                _get_generated_file_name(full_file_name, puml_type, definition_name, new_output_dir),
                os.path.join(new_output_dir, puml_type, f"{file_name}_{formatted_definition_name}{PLANT_UML_FILE_EXTENSION}"),
            )

    def test_puml_component_diagram_to_console(self):
        with temporary_test_file(TEST_PUML_ARCH_YAML, suffix=YAML_FILE_EXTENSION) as plugin_yaml:
            result = puml_component(plugin_yaml.name)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
            self._assert_component_diagram_content_full(result.output())

    def test_puml_component_diagram_to_file(self):
        with (TemporaryDirectory() as temp_directory,
              temporary_test_file(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=YAML_FILE_EXTENSION) as plugin_yaml):
            result = puml_component(plugin_yaml.name, temp_directory)

            full_output_dir = os.path.join(temp_directory, COMPONENT_STRING)
            self.assertIn(full_output_dir, result.output())
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            temp_directory_files = os.listdir(full_output_dir)
            expected_puml_file_paths = [
                _get_generated_file_name(plugin_yaml.name, COMPONENT_STRING, name)
                for name in [TEST_PUML_SYSTEM_NAME, TEST_PUML_SERVICE_ONE_TYPE, TEST_PUML_SERVICE_TWO_TYPE]
            ]
            [self.assertIn(os.path.basename(path), temp_directory_files) for path in expected_puml_file_paths]

            for path in expected_puml_file_paths:
                with open(path) as generated_puml_file:
                    content = generated_puml_file.read()
                    if TEST_PUML_SERVICE_ONE_TYPE.lower() in path:
                        self._assert_component_diagram_content_serviceone(content)
                    elif TEST_PUML_SERVICE_TWO_TYPE.lower() in path:
                        self._assert_component_diagram_content_servicetwo(content)
                    else:
                        self._assert_component_diagram_content_full(content)

    def test_puml_object_diagram_to_console(self):
        with temporary_test_file(TEST_PUML_ARCH_YAML, suffix=YAML_FILE_EXTENSION) as plugin_yaml:
            result = puml_object(plugin_yaml.name)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
            self._assert_object_diagram_content(result.output())

    def test_puml_object_diagram_to_file(self):
        with (TemporaryDirectory() as temp_directory,
              temporary_test_file(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=YAML_FILE_EXTENSION) as plugin_yaml):
            full_output_dir = os.path.join(temp_directory, OBJECT_STRING)

            result = puml_object(plugin_yaml.name, temp_directory)
            self.assertIn(full_output_dir, result.output())
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            temp_directory_files = os.listdir(full_output_dir)

            expected_puml_file_path = _get_generated_file_name(plugin_yaml.name, OBJECT_STRING, "")
            self.assertIn(os.path.basename(expected_puml_file_path), temp_directory_files)

            with open(os.path.join(temp_directory, expected_puml_file_path)) as generated_puml_file:
                self._assert_object_diagram_content(generated_puml_file.read())

    def test_puml_sequence_diagram_to_console(self):
        with temporary_test_file(TEST_PUML_ARCH_YAML, suffix=YAML_FILE_EXTENSION) as plugin_yaml:
            result = puml_sequence(plugin_yaml.name)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)
            self._assert_sequence_diagram_content_usecase_one(result.output())

    def test_puml_sequence_diagram_to_file(self):
        with (TemporaryDirectory() as temp_directory,
              temporary_test_file(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=YAML_FILE_EXTENSION) as plugin_yaml):
            result = puml_sequence(plugin_yaml.name, temp_directory)

            full_output_dir = os.path.join(temp_directory, SEQUENCE_STRING)
            self.assertIn(full_output_dir, result.output())
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            temp_directory_files = os.listdir(full_output_dir)
            expected_puml_file_paths = [
                _get_generated_file_name(plugin_yaml.name, SEQUENCE_STRING, name)
                for name in [TEST_PUML_USE_CASE_ONE_TITLE, TEST_PUML_USE_CASE_TWO_TITLE]
            ]
            [self.assertIn(os.path.basename(path), temp_directory_files) for path in expected_puml_file_paths]

            for path in expected_puml_file_paths:
                with open(path) as generated_puml_file:
                    content = generated_puml_file.read()
                    if _get_formatted_definition_name(TEST_PUML_USE_CASE_ONE_TITLE) in path:
                        self._assert_sequence_diagram_content_usecase_one(content)
                    elif _get_formatted_definition_name(TEST_PUML_USE_CASE_TWO_TITLE) in path:
                        self._assert_sequence_diagram_content_usecase_two(content)

    def _assert_component_diagram_content_full(self, component_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(component_diagram_content_string)
        self._assert_component_diagram_content_serviceone(component_diagram_content_string)
        self._assert_component_diagram_content_servicetwo(component_diagram_content_string)
        self.assertIn(f"package \"{TEST_PUML_SYSTEM_NAME}\"", component_diagram_content_string)

    def _assert_component_diagram_content_serviceone(self, component_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(component_diagram_content_string)
        self._assert_component_diagram_interface(component_diagram_content_string, [
            TEST_PUML_DATA_A_TYPE, TEST_PUML_DATA_B_TYPE
        ])
        self._assert_component_diagram_relations(component_diagram_content_string, "->", [
            {"left": TEST_PUML_DATA_A_TYPE, "right": f"[{TEST_PUML_SERVICE_ONE_TYPE}]", "name": "in"},
            {"left": f"[{TEST_PUML_SERVICE_ONE_TYPE}]", "right": TEST_PUML_DATA_B_TYPE, "name": "out"},
        ])

    def _assert_component_diagram_content_servicetwo(self, component_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(component_diagram_content_string)
        self._assert_component_diagram_interface(component_diagram_content_string, [
            TEST_PUML_DATA_B_TYPE, TEST_PUML_DATA_C_TYPE
        ])
        self._assert_component_diagram_relations(component_diagram_content_string, "->", [
            {"left": TEST_PUML_DATA_B_TYPE, "right": f"[{TEST_PUML_SERVICE_TWO_TYPE}]", "name": "in"},
            {"left": f"[{TEST_PUML_SERVICE_TWO_TYPE}]", "right": TEST_PUML_DATA_C_TYPE, "name": "out"},
        ])

    def _assert_component_diagram_interface(self, content: str, interfaces: list[str]):
        for interface in interfaces:
            self.assertIn(f"interface {interface}", content)

    def _assert_component_diagram_relations(self, content: str, relation: str, links: list[dict[str, str]]):
        for link in links:
            self.assertIn(f"{link.get('left')} {relation} {link.get('right')} : {link.get('name')}", content)

    def _assert_object_diagram_content(self, object_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(object_diagram_content_string)
        self._assert_object_diagram_object(object_diagram_content_string, [
            TEST_PUML_SYSTEM_NAME, TEST_PUML_SERVICE_ONE_TYPE, TEST_PUML_SERVICE_TWO_TYPE
        ])
        self._assert_object_diagram_object_relations(object_diagram_content_string, "*--", [
            {"left": TEST_PUML_SYSTEM_NAME, "right": TEST_PUML_SERVICE_ONE_TYPE},
            {"left": TEST_PUML_SYSTEM_NAME, "right": TEST_PUML_SERVICE_TWO_TYPE},
        ])

    def _assert_object_diagram_object(self, content: str, objects: list[str]):
        for obj in objects:
            self.assertIn(f"object {obj}", content)

    def _assert_object_diagram_object_relations(self, content: str, relation: str, relationships: list[dict[str, str]]):
        for relationship in relationships:
            self.assertIn(f"{relationship.get('left')} {relation} {relationship.get('right')}", content)

    def _assert_sequence_diagram_content_usecase_one(self, sequence_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(sequence_diagram_content_string)
        self.assertIn(f"title {TEST_PUML_USE_CASE_ONE_TITLE}", sequence_diagram_content_string)
        self._assert_sequence_diagram_participants(sequence_diagram_content_string, [
            {"name": TEST_PUML_SYSTEM_NAME, "type": TEST_PUML_SYSTEM_TYPE},
            {"name": TEST_PUML_SERVICE_ONE_NAME, "type": TEST_PUML_SERVICE_ONE_TYPE},
            {"name": TEST_PUML_SERVICE_TWO_NAME, "type": TEST_PUML_SERVICE_TWO_TYPE},
        ])
        self._assert_sequence_diagram_io(sequence_diagram_content_string, [
            {"in": TEST_PUML_SYSTEM_NAME, "out": TEST_PUML_SERVICE_ONE_NAME},
            {"in": TEST_PUML_SERVICE_TWO_NAME, "out": TEST_PUML_SYSTEM_NAME},
        ])

    def _assert_sequence_diagram_content_usecase_two(self, sequence_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(sequence_diagram_content_string)
        self.assertIn(f"title {TEST_PUML_USE_CASE_TWO_TITLE}", sequence_diagram_content_string)
        self._assert_sequence_diagram_participants(sequence_diagram_content_string, [
            {"name": TEST_PUML_SERVICE_ONE_NAME, "type": TEST_PUML_SERVICE_ONE_TYPE},
            {"name": TEST_PUML_SERVICE_TWO_NAME, "type": TEST_PUML_SERVICE_TWO_TYPE},
        ])
        self._assert_sequence_diagram_io(sequence_diagram_content_string, [
            {"in": TEST_PUML_SERVICE_ONE_NAME, "out": TEST_PUML_SERVICE_TWO_NAME},
            {"in": TEST_PUML_SERVICE_TWO_NAME, "out": TEST_PUML_SERVICE_ONE_NAME},
        ])

    def _assert_sequence_diagram_participants(self, content: str, participants: list[dict[str, str]]):
        for participant in participants:
            self.assertIn(f"participant {participant.get('type')} as {participant.get('name')}", content)

    def _assert_sequence_diagram_io(self, content: str, inputs_outputs: list[dict[str, str]]):
        for io in inputs_outputs:
            self.assertIn(f"{io.get('in')} -> {io.get('out')} : ", content)

    def _assert_diagram_contains_uml_boilerplate(self, puml_file):
        self.assertIn("@startuml", puml_file)
        self.assertIn("@enduml", puml_file)


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
TEST_PUML_USE_CASE_ONE_TITLE = "Nominal flow within the system."
TEST_PUML_USE_CASE_TWO_TITLE = "Sample request/response flow."

TEST_PUML_ARCH_YAML_SIMPLE_MODEL = f"""
model:
  name: {TEST_PUML_SERVICE_THREE_TYPE}
  behavior:
    - name: Do something with an {TEST_PUML_EXTERNAL_SYSTEM_TYPE}
      type: request-response
      description: Process data from {TEST_PUML_EXTERNAL_SYSTEM_TYPE}
      input:
        - name: in
          type: {TEST_PUML_DATA_C_TYPE}
      output:
        - name: out
          type: {TEST_PUML_DATA_A_TYPE}
      acceptance:
        - scenario: Receive {TEST_PUML_DATA_C_TYPE} request and return {TEST_PUML_DATA_A_TYPE} response
          given:
            - {TEST_PUML_EXTERNAL_SYSTEM_TYPE} is accessible
          when:
            - {TEST_PUML_SERVICE_THREE_TYPE} receives a {TEST_PUML_DATA_C_TYPE} request
          then:
            - {TEST_PUML_SERVICE_THREE_TYPE} returns the {TEST_PUML_DATA_A_TYPE} response
        - scenario: Receive invalid request
          given:
            - {TEST_PUML_SERVICE_THREE_TYPE} is accessible
          when:
            - {TEST_PUML_SERVICE_THREE_TYPE} receives request that isn't a {TEST_PUML_DATA_C_TYPE} request
          then:
            - {TEST_PUML_SERVICE_THREE_TYPE} returns an error response code
"""
TEST_PUML_ARCH_YAML_SIMPLE_USECASE = f"""
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
TEST_PUML_ARCH_YAML = f"""
model:
  name: {TEST_PUML_SYSTEM_NAME}
  description: A simple distributed system model
  components:
    - name: {TEST_PUML_SERVICE_ONE_NAME}
      type: {TEST_PUML_SERVICE_ONE_TYPE}
    - name: {TEST_PUML_SERVICE_TWO_NAME}
      type: {TEST_PUML_SERVICE_TWO_TYPE}
  behavior:
    - name: Process {TEST_PUML_DATA_A_TYPE} Request to {TEST_PUML_DATA_C_TYPE} Response
      type: request-response
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
      type: request-response
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
      type: request-response
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
data:
  name: {TEST_PUML_DATA_A_TYPE}
  fields:
  - name: msg
    type: string
---
data:
  name: {TEST_PUML_DATA_B_TYPE}
  fields:
  - name: msg
    type: string
---
data:
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
{TEST_PUML_ARCH_YAML_SIMPLE_USECASE}
"""
