Feature:  Constraint Assignment Arguments constraint

    Scenario:  Check the Shapes constraint spec
        Given I have the "./shapes/shapes.aac" model
        When I check the "./shapes/shapes.aac" model
        Then I should receive a message that the check was successful
