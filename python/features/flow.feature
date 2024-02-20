Feature:  Flow example model with usecase

    Scenario:  Check the flow system model
        Given I have the "./flow/System.yaml" model
        When I check the "./flow/System.yaml" model
        Then I should receive a message that the check was successful

    Scenario:  Check the flow usecase
        Given I have the "./flow/flow.yaml" model
        When I check the "./flow/flow.yaml" model
        Then I should receive a message that the check was successful