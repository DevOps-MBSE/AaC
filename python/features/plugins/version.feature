Feature: Version Evaluation

    Scenario: Get AaC Version
        When I run the "version" command with no arguments and with no flags
        Then I should receive a message that the command was successful
