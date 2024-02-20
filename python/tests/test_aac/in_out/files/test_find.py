from unittest import TestCase
from tempfile import TemporaryDirectory

from aac.in_out.files.find import find_aac_files, is_aac_file
from aac.context.language_context import LanguageContext

YAML_DOCUMENT_EXTENSION = "yaml"
AAC_DOCUMENT_EXTENSION = "aac"

class TestFindFiles(TestCase):

    def create_test_file(self, path: str, content: str) -> str:
        with open(path, "w") as test_file:
            test_file.write(content)
        return path
    
    def test_is_aac_file_with_valid_yaml_file(self):
        context = LanguageContext()
        test_file_content = context.get_aac_core_as_yaml()
        with TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.{YAML_DOCUMENT_EXTENSION}", test_file_content)
            actual_result = is_aac_file(test_yaml)

            self.assertTrue(actual_result)

    def test_is_aac_file_with_valid_aac_file(self):
        context = LanguageContext()
        test_file_content = context.get_aac_core_as_yaml()
        with TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.{AAC_DOCUMENT_EXTENSION}", test_file_content)
            actual_result = is_aac_file(test_yaml)

            self.assertTrue(actual_result)

    def test_is_aac_file_with_invalid_yaml_file(self):
        with TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.{YAML_DOCUMENT_EXTENSION}", VALID_NON_AAC_YAML_CONTENT)
            actual_result = is_aac_file(test_yaml)

            self.assertFalse(actual_result)

    def test_is_aac_file_with_invalid_aac_file(self):
        with TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.{AAC_DOCUMENT_EXTENSION}", VALID_NON_AAC_YAML_CONTENT)
            actual_result = is_aac_file(test_yaml)

            self.assertFalse(actual_result)

    def test_is_aac_file_with_invalid_file_extension(self):
        context = LanguageContext()
        test_file_content = context.get_aac_core_as_yaml()
        with TemporaryDirectory() as temp_dir:
            test_yaml = self.create_test_file(f"{temp_dir}/test.notYamlOrAac", test_file_content)
            actual_result = is_aac_file(test_yaml)

            self.assertFalse(actual_result)

    def test_find_aac_files(self):
        context = LanguageContext()
        with TemporaryDirectory() as l1_temp_dir:
            l1_aac_file_aac = self.create_test_file(f"{l1_temp_dir}/l1_aac_file.aac", context.get_aac_core_as_yaml())
            l1_invalid_file_aac = self.create_test_file(f"{l1_temp_dir}/l1_invalid_file.aac", VALID_NON_AAC_YAML_CONTENT)
        
            with TemporaryDirectory(dir=l1_temp_dir) as l2_temp_dir:
                l2_aac_file_yaml = self.create_test_file(f"{l2_temp_dir}/l2_aac_file.yaml", context.get_aac_core_as_yaml())
                l2_invalid_file_yaml = self.create_test_file(f"{l2_temp_dir}/l2_invalid_file.yaml", VALID_NON_AAC_YAML_CONTENT)

                with TemporaryDirectory(dir=l2_temp_dir) as l3_temp_dir:
                    l3_aac_file_aac = self.create_test_file(f"{l3_temp_dir}/l3_aac_file.yaml", context.get_aac_core_as_yaml())
                    l3_invalid_file_aac = self.create_test_file(f"{l3_temp_dir}/l3_invalid_file.yaml", VALID_NON_AAC_YAML_CONTENT)

                    expected_result = [l1_aac_file_aac, l2_aac_file_yaml, l3_aac_file_aac]
                    actual_result = find_aac_files(l1_temp_dir)

                    actual_result_file_paths = [file.uri for file in actual_result]
                    self.assertListEqual(expected_result, actual_result_file_paths)
                    self.assertNotIn(l1_invalid_file_aac, actual_result_file_paths)
                    self.assertNotIn(l2_invalid_file_yaml, actual_result_file_paths)
                    self.assertNotIn(l3_invalid_file_aac, actual_result_file_paths)


NON_YAML_FILE_CONTENT = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco
laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
"""

VALID_NON_AAC_YAML_CONTENT = """
apiVersion: xl-deploy/v1
kind: Infrastructure
spec:
- name: Infrastructure/Apache  host
  type: overthere.SshHost
  os: UNIX
  address: tomcat-host.local
  username: tomcatuser
- name: Infrastructure/local-docker
  type: docker.Engine
  dockerHost: http://dockerproxy:2375
- name: aws
  type: aws.Cloud
  accesskey: YOUR ACCESS KEY
  accessSecret: YOUR SECRET
"""
