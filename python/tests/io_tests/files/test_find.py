from unittest import TestCase
from tempfile import TemporaryDirectory

from aac.io.constants import YAML_DOCUMENT_EXTENSION, AAC_DOCUMENT_EXTENSION
from aac.io.files.find import find_aac_files, is_aac_file
from aac.lang.spec import get_aac_spec_as_yaml

from tests.helpers.io import temporary_test_file


class TestFindFiles(TestCase):
    def test_is_aac_file_with_valid_yaml_file(self):
        test_file_content = get_aac_spec_as_yaml()
        with temporary_test_file(test_file_content, suffix=YAML_DOCUMENT_EXTENSION) as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertTrue(actual_result)

    def test_is_aac_file_with_valid_aac_file(self):
        test_file_content = get_aac_spec_as_yaml()
        with temporary_test_file(test_file_content, suffix=AAC_DOCUMENT_EXTENSION) as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertTrue(actual_result)

    def test_is_aac_file_with_invalid_yaml_file(self):
        with temporary_test_file(VALID_NON_AAC_YAML_CONTENT, suffix=YAML_DOCUMENT_EXTENSION) as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertFalse(actual_result)

    def test_is_aac_file_with_invalid_aac_file(self):
        with temporary_test_file(NON_YAML_FILE_CONTENT, suffix=AAC_DOCUMENT_EXTENSION) as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertFalse(actual_result)

    def test_is_aac_file_with_invalid_file_extension(self):
        test_file_content = get_aac_spec_as_yaml()
        with temporary_test_file(test_file_content, suffix=".notYamlOrAac") as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertFalse(actual_result)

    def test_find_aac_files(self):

        with (
            TemporaryDirectory() as l1_temp_dir,
            temporary_test_file(get_aac_spec_as_yaml(), dir=l1_temp_dir, suffix=AAC_DOCUMENT_EXTENSION) as l1_aac_file_aac,
            temporary_test_file(
                VALID_NON_AAC_YAML_CONTENT, dir=l1_temp_dir, suffix=AAC_DOCUMENT_EXTENSION
            ) as l1_invalid_file_aac,
        ):

            with (
                TemporaryDirectory(dir=l1_temp_dir) as l2_temp_dir,
                temporary_test_file(
                    get_aac_spec_as_yaml(), dir=l2_temp_dir, suffix=YAML_DOCUMENT_EXTENSION
                ) as l2_aac_file_yaml,
                temporary_test_file(
                    VALID_NON_AAC_YAML_CONTENT, dir=l2_temp_dir, suffix=YAML_DOCUMENT_EXTENSION
                ) as l2_invalid_file_yaml,
            ):

                with (
                    TemporaryDirectory(dir=l2_temp_dir) as l3_temp_dir,
                    temporary_test_file(
                        get_aac_spec_as_yaml(), dir=l3_temp_dir, suffix=AAC_DOCUMENT_EXTENSION
                    ) as l3_aac_file_aac,
                    temporary_test_file(
                        VALID_NON_AAC_YAML_CONTENT, dir=l3_temp_dir, suffix=AAC_DOCUMENT_EXTENSION
                    ) as l3_invalid_file_aac,
                ):

                    expected_result = [l1_aac_file_aac.name, l2_aac_file_yaml.name, l3_aac_file_aac.name]
                    actual_result = find_aac_files(l1_temp_dir)

        actual_result_file_paths = [file.uri for file in actual_result]
        self.assertListEqual(expected_result, actual_result_file_paths)
        self.assertNotIn(l1_invalid_file_aac.name, actual_result_file_paths)
        self.assertNotIn(l2_invalid_file_yaml.name, actual_result_file_paths)
        self.assertNotIn(l3_invalid_file_aac.name, actual_result_file_paths)


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
