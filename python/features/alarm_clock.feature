Feature:  Alarm clock example model with usecase

    Scenario:  Check the alarm clock model
        Given I have the "./alarm_clock/alarm_clock.yaml" model
        When I check the "./alarm_clock/alarm_clock.yaml" model
        Then I should receive a message that the check was successful

    Scenario:  Check the alarm clock usecase
        Given I have the "./alarm_clock/usecase.yaml" model
        When I check the "./alarm_clock/usecase.yaml" model
        Then I should receive a message that the check was successful