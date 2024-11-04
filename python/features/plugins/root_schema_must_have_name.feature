Feature: Root Schema Must Have Name Evaluation

    Scenario: Check the root schema file
        Given I have the "./features/root_schema/root_schema.aac" file
        When I run the "check" command with arguments "./features/root_schema/root_schema.aac" and with no flags
        Then I should receive a message that the command was successful

    Scenario: Check the bad root schema file
        Given I have the "./features/root_schema/root_schema_bad.aac" file
        When I run the "check" command with arguments "./features/root_schema/root_schema_bad.aac" and with no flags
        Then I should receive a message that the command was not successful
