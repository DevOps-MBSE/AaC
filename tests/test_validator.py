import re
from unittest import TestCase

from aac import util, validator

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
    print(errors)
    for e in errors:
        assert re.search(pattern, e)


def assert_model_is_valid(model):
    "Assert that the provided MODEL is valid."
    assert_status_is_true(validator.is_valid(model))
    assert_no_errors(validator.get_all_errors(model))


def assert_model_is_invalid(model, error_pattern):
    "Assert that the provided MODEL is valid."
    assert_status_is_false(validator.is_valid(model))

    errors = validator.get_all_errors(model)
    assert_errors_exist(errors)
    assert_errors_contain(errors, error_pattern)


class ValidatorTest(TestCase):
    def test_can_validate_enums(self):
        assert_model_is_valid({"enum": {"name": "test", "values": []}})
        assert_model_is_valid({"enum": {"name": "test", "values": ["a"]}})
        assert_model_is_valid({"enum": {"name": "test", "values": ["a", "b", "c"]}})

        assert_model_is_invalid({"enum": {}}, ".*missing.*required.*(name|values).*")
        assert_model_is_invalid({"enum": {"name": "test"}}, ".*missing.*required.*values.*")
        assert_model_is_invalid({"enum": {"values": []}}, ".*missing.*required.*name.*")
        assert_model_is_invalid(
            {"enum": {"name": 1, "values": 2}}, ".*wrong.*type.*(name|values).*"
        )
