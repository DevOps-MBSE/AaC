Feature: Primitive Constraints

    Scenario: Check Primitives
        Given I have the "./primitives/primitives.yaml" model
        When I check the "./primitives/primitives.yaml" model
        Then I should receive a message that the check was successful
