Feature:  Counter example model

    Scenario:  Check the counter model
        Given I have the "./counter/Counter.yaml" model
        When I check the "./counter/Counter.yaml" model
        Then I should receive a message that the check was successful