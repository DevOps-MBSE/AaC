Feature: Check example models

# Alarm Clock

    Scenario:  Check the alarm clock model
        Given I have the "./alarm_clock/alarm_clock.yaml" model
        When I check the "./alarm_clock/alarm_clock.yaml" model
        Then I should receive a message that the check was successful

    Scenario:  Check the alarm clock usecase
        Given I have the "./alarm_clock/usecase.yaml" model
        When I check the "./alarm_clock/usecase.yaml" model with verbose
        Then I should receive a message that the check was successful

# Calculator

    Scenario:  Check the calculator spec
        Given I have the "./calc/spec/Calculator_SystemSpec.yaml" model
        When I check the "./calc/spec/Calculator_SystemSpec.yaml" model
        Then I should receive a message that the check was successful

    Scenario:  Check the calculator model
        Given I have the "./calc/model/calculator.yaml" model
        When I check the "./calc/model/calculator.yaml" model
        Then I should receive a message that the check was successful

# Counter

    Scenario:  Check the counter model
        Given I have the "./counter/Counter.yaml" model
        When I check the "./counter/Counter.yaml" model
        Then I should receive a message that the check was successful

# Docs examples

    Scenario:  Check the Definitions Example
        Given I have the "./docs_examples/dev_guide_language_api_definitions/acceptance_test.aac" model
        When I check the "./docs_examples/dev_guide_language_api_definitions/acceptance_test.aac" model
        Then I should receive a message that the check was successful

    Scenario:  Check the First Inheritance Example
        Given I have the "./docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_one.aac" model
        When I check the "./docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_one.aac" model
        Then I should receive a message that the check was successful

    Scenario:  Check the Second Inheritance Example
        Given I have the "./docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_two.aac" model
        When I check the "./docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_two.aac" model
        Then I should receive a message that the check was successful

    Scenario:  Check the All Possible Plugin Example
        Given I have the "./docs_examples/dev_guide_plugin_dev_guide/docs_all_possible.aac" model
        When I check the "./docs_examples/dev_guide_plugin_dev_guide/docs_all_possible.aac" model
        Then I should receive a message that the check was successful

    Scenario:  Check the Do Stuff Plugin Example
        Given I have the "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac" model
        When I check the "./docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac" model
        Then I should receive a message that the check was successful

# Echo

    Scenario:  Check the echo model
        Given I have the "./echo/EchoService.yaml" model
        When I check the "./echo/EchoService.yaml" model
        Then I should receive a message that the check was successful

# Flow

    Scenario:  Check the flow system model
        Given I have the "./flow/System.yaml" model
        When I check the "./flow/System.yaml" model
        Then I should receive a message that the check was successful

    Scenario:  Check the flow usecase
        Given I have the "./flow/flow.yaml" model
        When I check the "./flow/flow.yaml" model
        Then I should receive a message that the check was successful

# Shapes

    Scenario:  Check the flow system model
        Given I have the "./shapes/shapes.aac" model
        When I check the "./shapes/shapes.aac" model
        Then I should receive a message that the check was successful
