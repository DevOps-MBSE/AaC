Feature:  Echo server example model

    Scenario:  Check the echo model
        Given I have the "./echo/EchoService.yaml" model
        When I check the "./echo/EchoService.yaml" model
        Then I should receive a message that the check was successful