Feature:  If True Then Empty Evaluation

    Scenario:  Check the Schema Plugin File
        Given I have the "./features/plugin_examples/schema_plugin.aac" file
        When I run the "check" command with arguments "./features/examples/schema_plugin.aac" and with no flags
        Then I should receive a message that the command was successful

    Scenario:  Check the Bad Schema Plugin File
        Given I have the "./features/plugin_examples/schema_plugin_bad.aac" file
        When I run the "check" command with arguments "./features/examples/schema_plugin_bad.aac" and with no flags
        Then I should receive a message that the command was not successful
