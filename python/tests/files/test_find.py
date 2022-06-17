from unittest import TestCase
from tempfile import NamedTemporaryFile, TemporaryDirectory

from aac.files.find import find_aac_files, is_aac_file
from aac.spec.core import get_aac_spec_as_yaml

from tests.helpers.io import temporary_test_file, YAML_FILE_EXTENSION, AAC_FILE_EXTENSION


class TestFindFiles(TestCase):

    def test_is_aac_file_with_valid_yaml_file(self):
        test_file_content = get_aac_spec_as_yaml()
        with temporary_test_file(test_file_content, suffix=YAML_FILE_EXTENSION) as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertTrue(actual_result)

    def test_is_aac_file_with_valid_aac_file(self):
        test_file_content = get_aac_spec_as_yaml()
        with temporary_test_file(test_file_content, suffix=AAC_FILE_EXTENSION) as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertTrue(actual_result)

    def test_is_aac_file_with_invalid_yaml_file(self):
        with temporary_test_file(INVALID_AAC_FILE_CONTENT, suffix=YAML_FILE_EXTENSION) as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertFalse(actual_result)

    def test_is_aac_file_with_invalid_aac_file(self):
        with temporary_test_file(INVALID_AAC_FILE_CONTENT, suffix=AAC_FILE_EXTENSION) as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertFalse(actual_result)

    def test_is_aac_file_with_invalid_file_extension(self):
        test_file_content = get_aac_spec_as_yaml()
        with temporary_test_file(test_file_content, suffix=".notYamlOrAac") as test_yaml:
            actual_result = is_aac_file(test_yaml.name)

        self.assertFalse(actual_result)

    def test_find_aac_files(self):

        with TemporaryDirectory() as l1_temp_dir:
            l1_aac_file_aac = NamedTemporaryFile(dir=l1_temp_dir, suffix=AAC_FILE_EXTENSION, mode="w")
            _write_content_to_temp_file(l1_aac_file_aac, get_aac_spec_as_yaml())

            l1_invalid_file_aac = NamedTemporaryFile(dir=l1_temp_dir, suffix=AAC_FILE_EXTENSION, mode="w")
            _write_content_to_temp_file(l1_invalid_file_aac, INVALID_AAC_FILE_CONTENT)

            with TemporaryDirectory(dir=l1_temp_dir) as l2_temp_dir:
                l2_aac_file_yaml = NamedTemporaryFile(dir=l2_temp_dir, suffix=YAML_FILE_EXTENSION, mode="w")
                _write_content_to_temp_file(l2_aac_file_yaml, get_aac_spec_as_yaml())

                l2_invalid_file_yaml = NamedTemporaryFile(dir=l2_temp_dir, suffix=YAML_FILE_EXTENSION, mode="w")
                _write_content_to_temp_file(l2_invalid_file_yaml, INVALID_AAC_FILE_CONTENT)

                with TemporaryDirectory(dir=l2_temp_dir) as l3_temp_dir:
                    l3_aac_file_aac = NamedTemporaryFile(dir=l3_temp_dir, suffix=AAC_FILE_EXTENSION, mode="w")
                    _write_content_to_temp_file(l3_aac_file_aac, get_aac_spec_as_yaml())

                    l3_invalid_file_aac = NamedTemporaryFile(dir=l3_temp_dir, suffix=AAC_FILE_EXTENSION, mode="w")
                    _write_content_to_temp_file(l3_invalid_file_aac, INVALID_AAC_FILE_CONTENT)

                    expected_result = [l1_aac_file_aac.name, l2_aac_file_yaml.name, l3_aac_file_aac.name]
                    actual_result = find_aac_files(l1_temp_dir)

        self.assertListEqual(expected_result, actual_result)
        self.assertNotIn(l1_invalid_file_aac.name, actual_result)
        self.assertNotIn(l2_invalid_file_yaml.name, actual_result)
        self.assertNotIn(l3_invalid_file_aac.name, actual_result)


def _write_content_to_temp_file(temp_file, content: str) -> None:
    temp_file.write(content)
    temp_file.seek(0)


INVALID_AAC_FILE_CONTENT = """
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
