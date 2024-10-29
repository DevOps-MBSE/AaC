"""General purpose steps for the behave print_defs tests."""""
from behave import then


@then('I should receive a list of definitions to the terminal')
def print_defs_result(context):
    """
    Ensure the definitions were returned correctly.

    Args:
        context: Active context to check against.
    """
    assert context.exit_code == 0
    assert len(context.output_message) > 1

    assert "name: Exclusive Fields" in context.output_message
    assert "name: No Extends for Final" in context.output_message
    assert "name: AacType" in context.output_message
    assert "name: Modifier" in context.output_message


@then('I should receive a list of core definitions to the terminal')
def print_defs_result_core_only(context):
    """
    Ensure the definitions were returned correctly.

    Args:
        context: Active context to check against.
    """
    assert context.exit_code == 0
    assert len(context.output_message) > 1

    assert "name: Exclusive Fields" not in context.output_message
    assert "name: No Extends for Final" not in context.output_message
    assert "name: AacType" in context.output_message
    assert "name: Modifier" in context.output_message
