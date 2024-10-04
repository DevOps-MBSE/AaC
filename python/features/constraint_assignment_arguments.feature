Feature:  Constraint Assignment Arguments Constraint Evaluation

    Scenario:  Check the Shapes constraint spec
        Given I have the "./shapes/shapes.aac" model
        When I check the "./shapes/shapes.aac" model
        Then I should receive a message that the check was successful

    Scenario:  Check the Bad Shapes constraint spec
        Given I have the "./shapes/bad_shapes.aac" model
        When I check the "./shapes/bad_shapes.aac" bad model
        Then I should receive a message that the check was not successful
