Feature: Primitive Constraints

    Scenario: Check Primitives
        Given I have the "./features/primitives/primitives.yaml" file
        When I run the "check" command with arguments "./features/primitives/primitives.yaml" and no flags
        Then I should receive a message that the command was successful

    Scenario: Check Bad Bool
        Given I have the "./features/primitives/bad_bool.yaml" file
        When I run the "check" command with arguments "./features/primitives/bad_bool.yaml" and no flags
        Then I should receive a message that the command was not successful

    Scenario: Check Bad Date
        Given I have the "./features/primitives/bad_date.yaml" file
        When I run the "check" command with arguments "./features/primitives/bad_date.yaml" and no flags
        Then I should receive a message that the command was not successful

    Scenario: Check Bad Directory
        Given I have the "./features/primitives/bad_dir.yaml" file
        When I run the "check" command with arguments "./features/primitives/bad_dir.yaml" and no flags
        Then I should receive a message that the command was not successful

    Scenario: Check Bad File
        Given I have the "./features/primitives/bad_file.yaml" file
        When I run the "check" command with arguments "./features/primitives/bad_file.yaml" and no flags
        Then I should receive a message that the command was not successful

    Scenario: Check Bad String
        Given I have the "./features/primitives/bad_string.yaml" file
        When I run the "check" command with arguments "./features/primitives/bad_string.yaml" and no flags
        Then I should receive a message that the command was not successful

    Scenario: Check Bad Integer
        Given I have the "./features/primitives/bad_int.yaml" file
        When I run the "check" command with arguments "./features/primitives/bad_int.yaml" and no flags
        Then I should receive a message that the command was not successful

    Scenario: Check Bad Number
        Given I have the "./features/primitives/bad_number.yaml" file
        When I run the "check" command with arguments "./features/primitives/bad_number.yaml" and no flags
        Then I should receive a message that the command was not successful

    Scenario: Check Bad Dataref
        Given I have the "./features/primitives/bad_dataref.yaml" file
        When I run the "check" command with arguments "./features/primitives/bad_dataref.yaml" and no flags
        Then I should receive a message that the command was not successful

    Scenario: Check Bad Typeref
        Given I have the "./features/primitives/bad_typeref.yaml" file
        When I run the "check" command with arguments "./features/primitives/bad_typeref.yaml" and no flags
        Then I should receive a message that the command was not successful
