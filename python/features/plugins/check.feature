Feature: Check example models

# Alarm Clock

    Scenario:  Check the alarm clock model
        Given I have the "./features/alarm_clock/alarm_clock.yaml" file
        When I run the "check" command with arguments "./features/alarm_clock/alarm_clock.yaml" and with no flags
        Then I should receive a message that the command was successful

    Scenario:  Check the alarm clock usecase
        Given I have the "./features/alarm_clock/usecase.yaml" file
        When I run the "check" command with arguments "./features/alarm_clock/usecase.yaml" and with flags "--verbose"
        Then I should receive a message that the command was successful
        And I should receive a list of successfully evaluated models

# Calculator

    Scenario:  Check the calculator spec
        Given I have the "./features/calc/spec/Calculator_SystemSpec.yaml" file
        When I run the "check" command with arguments "./features/calc/spec/Calculator_SystemSpec.yaml" and with no flags
        Then I should receive a message that the command was successful

    Scenario:  Check the calculator model
        Given I have the "./features/calc/model/calculator.yaml" file
        When I run the "check" command with arguments "./features/calc/model/calculator.yaml" and with flags "--verbose"
        Then I should receive a message that the command was successful
        And I should receive a list of successfully evaluated models

# Counter

    Scenario:  Check the counter model
        Given I have the "./features/counter/Counter.yaml" file
        When I run the "check" command with arguments "./features/counter/Counter.yaml" and with flags "--verbose"
        Then I should receive a message that the command was successful
        And I should receive a list of successfully evaluated models

# Docs examples

    Scenario:  Check the Definitions Example
        Given I have the "./features/docs_examples/dev_guide_language_api_definitions/acceptance_test.aac" file
        When I run the "check" command with arguments "./features/docs_examples/dev_guide_language_api_definitions/acceptance_test.aac" and with no flags
        Then I should receive a message that the command was successful

    Scenario:  Check the First Inheritance Example
        Given I have the "./features/docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_one.aac" file
        When I run the "check" command with arguments "./features/docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_one.aac" and with flags "--verbose"
        Then I should receive a message that the command was successful
        And I should receive a list of successfully evaluated models

    Scenario:  Check the Second Inheritance Example
        Given I have the "./features/docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_two.aac" file
        When I run the "check" command with arguments "./features/docs_examples/dev_guide_language_api_modeling_inheritance/docs_inheritance_two.aac" and with no flags
        Then I should receive a message that the command was successful

    Scenario:  Check the All Possible Plugin Example
        Given I have the "./features/docs_examples/dev_guide_plugin_dev_guide/docs_all_possible.aac" file
        When I run the "check" command with arguments "./features/docs_examples/dev_guide_plugin_dev_guide/docs_all_possible.aac" and with no flags
        Then I should receive a message that the command was successful

    Scenario:  Check the Do Stuff Plugin Example
        Given I have the "./features/docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac" file
        When I run the "check" command with arguments "./features/docs_examples/dev_guide_plugin_dev_guide/docs_do_stuff.aac" and with no flags
        Then I should receive a message that the command was successful

# Echo

    Scenario:  Check the echo model
        Given I have the "./features/echo/EchoService.yaml" file
        When I run the "check" command with arguments "./features/echo/EchoService.yaml" and with flags "--verbose"
        Then I should receive a message that the command was successful
        And I should receive a list of successfully evaluated models

# Flow

    Scenario:  Check the flow system model
        Given I have the "./features/flow/System.yaml" file
        When I run the "check" command with arguments "./features/flow/System.yaml" and with no flags
        Then I should receive a message that the command was successful

    Scenario:  Check the flow usecase
        Given I have the "./features/flow/flow.yaml" file
        When I run the "check" command with arguments "./features/flow/flow.yaml" and with flags "--verbose"
        Then I should receive a message that the command was successful
        And I should receive a list of successfully evaluated models

# Shapes

    Scenario:  Check the flow system model
        Given I have the "./features/shapes/shapes.aac" file
        When I run the "check" command with arguments "./features/shapes/shapes.aac" and with flags "--verbose"
        Then I should receive a message that the command was successful
        And I should receive a list of successfully evaluated models

# Trade study

    Scenario: Check the trade study files
        Given I have the "./features/trade_study/doc/cookie_trade_study.aac" file
        When I run the "check" command with arguments "./features/shapes/shapes.aac" and with flags "--verbose"
        Then I should receive a message that the command was successful
        And I should receive a list of successfully evaluated models
