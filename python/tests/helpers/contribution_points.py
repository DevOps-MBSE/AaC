from typing import Any, Callable
from unittest.case import TestCase

from aac.cli.aac_command import AacCommand, AacCommandArgument
from aac.lang.definitions.definition import Definition
from aac.plugins.contribution_points import InvalidContributionPointError
from aac.plugins.validators._validator_plugin import ValidatorPlugin


def identity(value: object) -> object:
    """Return the object that was passed in."""
    return value


def create_command(
    name: str, description: str = "", callback: Callable = identity, args: list[AacCommandArgument] = []
) -> AacCommand:
    """Create a new AacCommand for testing."""
    return AacCommand(name, description, callback, args)


def create_validation(name: str, definition: Definition, callback: Callable = identity) -> ValidatorPlugin:
    """Create a new ValidatorPlugin for testing."""
    return ValidatorPlugin(name, definition, callback)


def assert_items_are_registered(
    test_case: TestCase, items: list, register_fn: Callable[[list], None], get_registered_items_fn: Callable[[], list]
):
    """Assert that the specified items are registered."""
    register_fn(items)

    registered_items = get_registered_items_fn()
    test_case.assertEqual(len(items), len(registered_items))
    [test_case.assertIn(item, registered_items) for item in items]


def assert_invalid_contribution_point(
    test_case: TestCase, plugin_name: str, item: object, register_fn: Callable[[str, Any], None], exception_regex: str
):
    """Assert that attempting to register the specified item results in an error."""
    with test_case.assertRaises(InvalidContributionPointError) as cm:
        register_fn(plugin_name, item)

    test_case.assertRegex(cm.exception.message.lower(), exception_regex)
