Feature:  Calculator example model with requirements

    Scenario:  Check the calculator spec
        Given I have the "./calc/spec/Calculator_SystemSpec.yaml" model
        When I check the "./calc/spec/Calculator_SystemSpec.yaml" model
        Then I should receive a message that the check was successful

    Scenario:  Check the calculator model
        Given I have the "./calc/model/calculator.yaml" model
        When I check the "./calc/model/calculator.yaml" model
        Then I should receive a message that the check was successful