Feature: Primitive Constraints

    Scenario: Check Primitives
        Given I have the "./primitives/primitives.yaml" model
        When I check the "./primitives/primitives.yaml" model
        Then I should receive a message that the check was successful

    Scenario: Check Bad Bool
        Given I have the "./primitives/bad_bool.yaml" model
        When I check the "./primitives/bad_bool.yaml" bad model
        Then I should receive a message that the check was not successful

    Scenario: Check Bad Date
        Given I have the "./primitives/bad_date.yaml" model
        When I check the "./primitives/bad_date.yaml" bad model
        Then I should receive a message that the check was not successful

    Scenario: Check Bad Directory
        Given I have the "./primitives/bad_dir.yaml" model
        When I check the "./primitives/bad_dir.yaml" bad model
        Then I should receive a message that the check was not successful

    Scenario: Check Bad File
        Given I have the "./primitives/bad_file.yaml" model
        When I check the "./primitives/bad_file.yaml" bad model
        Then I should receive a message that the check was not successful

    Scenario: Check Bad String
        Given I have the "./primitives/bad_string.yaml" model
        When I check the "./primitives/bad_string.yaml" bad model
        Then I should receive a message that the check was not successful

    Scenario: Check Bad Integer
        Given I have the "./primitives/bad_int.yaml" model
        When I check the "./primitives/bad_int.yaml" bad model
        Then I should receive a message that the check was not successful

    Scenario: Check Bad Number
        Given I have the "./primitives/bad_number.yaml" model
        When I check the "./primitives/bad_number.yaml" bad model
        Then I should receive a message that the check was not successful

    Scenario: Check Bad Dataref
        Given I have the "./primitives/bad_dataref.yaml" model
        When I check the "./primitives/bad_dataref.yaml" bad model
        Then I should receive a message that the check was not successful

    Scenario: Check Bad Typeref
        Given I have the "./primitives/bad_typeref.yaml" model
        When I check the "./primitives/bad_typeref.yaml" bad model
        Then I should receive a message that the check was not successful
