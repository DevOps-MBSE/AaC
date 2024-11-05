Feature:  Unique Root Keys Evaluation

    Scenario:  Check the Root Keys example file
        Given I have the "./features/plugin_examples/root_keys.aac" file
        When I run the "check" command with arguments "./features/plugin_examples/root_keys.aac" and with no flags
        Then I should receive a message that the command was successful

    Scenario:  Check the Root Keys Duplicate example file
        Given I have the "./features/plugin_examples/root_keys_duplicate.aac" file
        When I run the "check" command with arguments "./features/plugin_examples/root_keys_duplicate.aac" and with no flags
        Then I should receive a message that the command was not successful
