Feature:  Print-Defs Evaluation

    Scenario: Print Definitions from Context
        When I run the "print-defs" command with no arguments and with no flags
        Then I should receive a list of definitions to the terminal

    Scenario: Print Definitions from Context with Core-Only
        When I run the "print-defs" command with no arguments and with flags "--core-only"
        Then I should receive a list of core definitions to the terminal
