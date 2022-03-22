"""Provide some general unit test assertion helpers to address recurring and duplicated testing patterns"""
from aac.plugins.plugin_execution import (
    PluginExecutionResult,
    PluginExecutionStatusCode
)


def assert_plugin_success(plugin_result: PluginExecutionResult):
    """
    Asserts that the plugin result indicates success.

    In the event that the plugin status is successful, print the error
    messages in the assertion message.
    """

    if plugin_result.status_code != PluginExecutionStatusCode.SUCCESS:
        raise AssertionError(f"PluginResult did not return success as expected:\n{plugin_result.messages}")

