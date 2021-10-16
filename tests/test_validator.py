import re
from unittest import TestCase

from aac import util, validator, parser

assert_status_is_false = lambda status: assert_status_is(status, False)
assert_status_is_true = lambda status: assert_status_is(status, True)


def assert_status_is(status, expected_status):
    """Assert STATUS is EXPECTED_STATUS."""
    assert status is expected_status


def assert_errors_exist(errors):
    """Assert that ERRORS is a non-empty collection."""
    assert len(errors) > 0


def assert_no_errors(errors):
    """Assert that ERRORS is an empty collection."""
    assert len(errors) == 0


def assert_errors_contain(errors, pattern):
    """Assert that at least one error in ERRORS matches PATTERN."""
    for e in errors:
        assert re.search(pattern, e)


class ValidatorTest(TestCase):
    def test_validation_succeeds_for_valid_enum(self):
        status, errors = validator._validate_general(
            {"enum": {"name": "test", "values": ["a", "b"]}}
        )

        assert_status_is_true(status)
        assert_no_errors(errors)

    def test_validation_succeeds_for_valid_data(self):
        status, errors = validator._validate_general(
            {"data": {"name": "test", "fields": [{"name": "a", "type": "number"}]}}
        )

        assert_status_is_true(status)
        assert_no_errors(errors)

    def test_validation_succeeds_for_minimal_valid_model(self):
        status, errors = validator._validate_general({"model": {"name": "test", "behavior": []}})

        assert_status_is_true(status)
        assert_no_errors(errors)

    def test_validation_fails_when_model_has_unrecognized_fields(self):
        status, errors = validator._validate_model_entry(
            "data",
            "data",
            {"name": "test", "fields": {}, "unrecognized": "key"},
            *util.get_aac_spec(),
        )

        assert_status_is_false(status)
        assert_errors_exist(errors)
        assert_errors_contain(errors, "unrecognized.*field.*unrecognized")

    def test_validation_fails_when_model_has_more_than_one_root_item(self):
        status, errors = validator._validate_general({"a": 1, "b": 2})

        assert_status_is_false(status)
        assert_errors_exist(errors)
        assert_errors_contain(errors, "more.*one.*root")

    def test_validation_fails_when_model_has_unknown_root(self):
        status, errors = validator._validate_general({"a": 1})

        assert_status_is_false(status)
        assert_errors_exist(errors)
        assert_errors_contain(errors, "unrecognized.*root.*[a]")

    def test_data_validation(self):

        valid_data = """
        data:
            name: MyTestFieldType
            fields:
                - name: name
                  type: string
                - name: type
                  type: string
            required:
                - name
                - type
        """
        validate_me = parser.parse_str(valid_data, "test_validator.test_datavalidation", False)
        status, errors = validator.validate(validate_me)

        if not status:
            print(f"Failed to validate with errors: {errors}")

        assert_status_is_true(status)
        assert_no_errors(errors)
