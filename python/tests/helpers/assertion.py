"""Provide some general unit test assertion helpers to address recurring and duplicated testing patterns."""
from aac.plugins.plugin_execution import (
    PluginExecutionResult,
    PluginExecutionStatusCode
)


def assert_plugin_success(plugin_result: PluginExecutionResult):
    """
    Asserts that the plugin result indicates a plugin failure status.

    In the event that the plugin status does not match the expected value,
    print the error messages in the assertion message.
    """
    _assert_plugin_state(plugin_result, PluginExecutionStatusCode.SUCCESS)


def assert_plugin_failure(plugin_result: PluginExecutionResult):
    """
    Asserts that the plugin result indicates a plugin failure status.

    In the event that the plugin status does not match the expected value,
    print the error messages in the assertion message.
    """
    _assert_plugin_state(plugin_result, PluginExecutionStatusCode.PLUGIN_FAILURE)


def assert_general_failure(plugin_result: PluginExecutionResult):
    """
    Asserts that the plugin result indicates a general failure status.

    In the event that the plugin status does not match the expected value,
    print the error messages in the assertion message.
    """
    _assert_plugin_state(plugin_result, PluginExecutionStatusCode.GENERAL_FAILURE)


def _assert_plugin_state(plugin_result: PluginExecutionResult, code: PluginExecutionStatusCode):
    if plugin_result.status_code != code:
        raise AssertionError(f"PluginResult did not return {code} as expected. Messages:\n{plugin_result.messages}")
