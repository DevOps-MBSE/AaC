Feature:  Constraint Assignment Arguments Constraint Evaluation

    Scenario:  Check the Shapes constraint spec
        Given I have the "./features/shapes/shapes.aac" file
        When I run the "check" command with arguments "./features/shapes/shapes.aac" and with no flags
        Then I should receive a message that the command was successful

    Scenario:  Check the Bad Shapes constraint spec
        Given I have the "./features/shapes/bad_shapes.aac" file
        When I run the "check" command with arguments "./features/shapes/bad_shapes.aac" and with no flags
        Then I should receive a message that the command was not successful
