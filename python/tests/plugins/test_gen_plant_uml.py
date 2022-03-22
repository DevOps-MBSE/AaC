import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from aac.plugins.gen_plant_uml.gen_plant_uml_impl import (
    COMPONENT_STRING,
    OBJECT_STRING,
    SEQUENCE_STRING,
    PLANT_UML_FILE_EXTENSION,
    puml_component,
    puml_object,
    puml_sequence,
)
from aac.plugins.plugin_execution import PluginExecutionStatusCode
from tests.helpers.io import temporary_test_file


class TestGenPlantUml(TestCase):
    def test_puml_component_diagram_to_console(self):
        with (TemporaryDirectory() as temp_directory,
              temporary_test_file(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=".yaml") as plugin_yaml):
            result = puml_component(plugin_yaml.name)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            puml_content = "\n".join(result.messages)
            self._assert_diagram_contains_uml_boilerplate(puml_content)
            self._assert_component_diagram_content(puml_content)

    def test_puml_component_diagram_to_file(self):
        with (TemporaryDirectory() as temp_directory,
              temporary_test_file(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=".yaml") as plugin_yaml):
            # Get the rng temp AaC file name, but with a puml extension
            expected_puml_file_path = self._get_expected_puml_file_name(plugin_yaml.name, COMPONENT_STRING)

            result = puml_component(plugin_yaml.name, temp_directory)
            self.assertIn(expected_puml_file_path, "\n".join(result.messages))
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            temp_directory_files = os.listdir(temp_directory)

            self.assertIn(expected_puml_file_path, temp_directory_files)

            with open(os.path.join(temp_directory, expected_puml_file_path)) as generated_puml_file:
                generated_puml_file_content = generated_puml_file.read()
                self._assert_diagram_contains_uml_boilerplate(generated_puml_file_content)
                self._assert_component_diagram_content(generated_puml_file_content)

    def test_puml_object_diagram_to_console(self):
        with (TemporaryDirectory() as temp_directory,
              temporary_test_file(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=".yaml") as plugin_yaml):
            result = puml_object(plugin_yaml.name)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            puml_content = "\n".join(result.messages)
            self._assert_diagram_contains_uml_boilerplate(puml_content)
            self._assert_object_diagram_content(puml_content)

    def test_puml_object_diagram_to_file(self):
        with (TemporaryDirectory() as temp_directory,
              temporary_test_file(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=".yaml") as plugin_yaml):
            # Get the rng temp AaC file name, but with a puml extension
            expected_puml_file_path = self._get_expected_puml_file_name(plugin_yaml.name, OBJECT_STRING)

            result = puml_object(plugin_yaml.name, temp_directory)
            self.assertIn(expected_puml_file_path, "\n".join(result.messages))
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            temp_directory_files = os.listdir(temp_directory)

            self.assertIn(expected_puml_file_path, temp_directory_files)

            with open(os.path.join(temp_directory, expected_puml_file_path)) as generated_puml_file:
                generated_puml_file_content = generated_puml_file.read()
                self._assert_diagram_contains_uml_boilerplate(generated_puml_file_content)
                self._assert_object_diagram_content(generated_puml_file_content)

    def test_puml_sequence_diagram_to_console(self):
        with (TemporaryDirectory() as temp_directory,
              temporary_test_file(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=".yaml") as plugin_yaml):
            result = puml_sequence(plugin_yaml.name)
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            puml_content = "\n".join(result.messages)
            self._assert_diagram_contains_uml_boilerplate(puml_content)
            self._assert_sequence_diagram_content(puml_content)

    def test_puml_sequence_diagram_to_file(self):
        with (TemporaryDirectory() as temp_directory,
              temporary_test_file(TEST_PUML_ARCH_YAML, dir=temp_directory, suffix=".yaml") as plugin_yaml):
            # Get the rng temp AaC file name, but with a puml extension
            expected_puml_file_path = self._get_expected_puml_file_name(plugin_yaml.name, SEQUENCE_STRING)

            result = puml_sequence(plugin_yaml.name, temp_directory)
            self.assertIn(expected_puml_file_path, "\n".join(result.messages))
            self.assertEqual(result.status_code, PluginExecutionStatusCode.SUCCESS)

            temp_directory_files = os.listdir(temp_directory)

            self.assertIn(expected_puml_file_path, temp_directory_files)

            with open(os.path.join(temp_directory, expected_puml_file_path)) as generated_puml_file:
                generated_puml_file_content = generated_puml_file.read()
                self._assert_diagram_contains_uml_boilerplate(generated_puml_file_content)
                self._assert_sequence_diagram_content(generated_puml_file_content)

    def _assert_component_diagram_content(self, component_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(component_diagram_content_string)
        self.assertIn(f"interface {TEST_PUML_DATA_A_TYPE}", component_diagram_content_string)
        self.assertIn(f"interface {TEST_PUML_DATA_B_TYPE}", component_diagram_content_string)
        self.assertIn(f"interface {TEST_PUML_DATA_C_TYPE}", component_diagram_content_string)
        self.assertIn(f"package \"{TEST_PUML_SYSTEM_NAME}\"", component_diagram_content_string)
        self.assertIn(f"{TEST_PUML_DATA_A_TYPE} -> [{TEST_PUML_SERVICE_ONE_TYPE}] : in", component_diagram_content_string)
        self.assertIn(f"[{TEST_PUML_SERVICE_ONE_TYPE}] -> {TEST_PUML_DATA_B_TYPE} : out", component_diagram_content_string)

    def _assert_object_diagram_content(self, object_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(object_diagram_content_string)
        self.assertIn(f"object {TEST_PUML_SYSTEM_NAME}", object_diagram_content_string)
        self.assertIn(f"object {TEST_PUML_SERVICE_ONE_TYPE}", object_diagram_content_string)
        self.assertIn(f"object {TEST_PUML_SERVICE_TWO_TYPE}", object_diagram_content_string)
        self.assertIn(f"{TEST_PUML_SYSTEM_NAME} *-- {TEST_PUML_SERVICE_ONE_TYPE}", object_diagram_content_string)
        self.assertIn(f"{TEST_PUML_SYSTEM_NAME} *-- {TEST_PUML_SERVICE_TWO_TYPE}", object_diagram_content_string)

    def _assert_sequence_diagram_content(self, sequence_diagram_content_string: str):
        self._assert_diagram_contains_uml_boilerplate(sequence_diagram_content_string)
        self.assertIn(f"title {TEST_PUML_USE_CASE_ONE_TITLE}", sequence_diagram_content_string)
        self.assertIn(f"participant {TEST_PUML_SYSTEM_TYPE} as {TEST_PUML_SYSTEM_NAME}", sequence_diagram_content_string)
        self.assertIn(f"participant {TEST_PUML_SERVICE_ONE_TYPE} as {TEST_PUML_SERVICE_ONE_NAME}", sequence_diagram_content_string)
        self.assertIn(f"participant {TEST_PUML_SERVICE_TWO_TYPE} as {TEST_PUML_SERVICE_TWO_NAME}", sequence_diagram_content_string)
        self.assertIn(f"{TEST_PUML_SYSTEM_NAME} -> {TEST_PUML_SERVICE_ONE_NAME} : ", sequence_diagram_content_string)
        self.assertIn(f"{TEST_PUML_SERVICE_TWO_NAME} -> {TEST_PUML_SYSTEM_NAME} : ", sequence_diagram_content_string)

    def _assert_diagram_contains_uml_boilerplate(self, puml_file):
        self.assertIn("@startuml", puml_file)
        self.assertIn("@enduml", puml_file)

    def _get_expected_puml_file_name(self, plugin_architecture_file: str, puml_type: str) -> str:
        return os.path.basename(plugin_architecture_file).replace(".yaml", f"_{puml_type}{PLANT_UML_FILE_EXTENSION}")


TEST_PUML_SYSTEM_NAME = "Test-System"
TEST_PUML_SYSTEM_TYPE = "System"
TEST_PUML_SERVICE_ONE_NAME = "svc1"
TEST_PUML_SERVICE_ONE_TYPE = "ServiceOne"
TEST_PUML_SERVICE_TWO_NAME = "svc2"
TEST_PUML_SERVICE_TWO_TYPE = "ServiceTwo"
TEST_PUML_DATA_A_TYPE = "DataA"
TEST_PUML_DATA_B_TYPE = "DataB"
TEST_PUML_DATA_C_TYPE = "DataC"
TEST_PUML_USE_CASE_ONE_TITLE = "Nominal flow within the system."
TEST_PUML_USE_CASE_TWO_TITLE = "Sample request/response flow."

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
usecase:
  name: {TEST_PUML_USE_CASE_TWO_TITLE}
  description:
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
